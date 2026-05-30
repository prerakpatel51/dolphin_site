import time
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.utils import timezone

from api.email_queue import process_email_recipient, update_job_after_batch
from api.models import EmailDeliveryJob, EmailDeliveryRecipient


class Command(BaseCommand):
    help = "Process queued email delivery jobs."

    def add_arguments(self, parser):
        parser.add_argument("--once", action="store_true", help="Process available work once and exit.")
        parser.add_argument("--sleep", type=float, default=5.0, help="Seconds to wait between polling attempts.")
        parser.add_argument("--batch-size", type=int, default=25, help="Maximum recipients to send per polling cycle.")
        parser.add_argument("--workers", type=int, default=0, help="Parallel email sends per polling cycle. 0 chooses a database-safe default.")
        parser.add_argument("--stale-minutes", type=int, default=10, help="Retry recipients stuck in sending longer than this many minutes.")
        parser.add_argument("--max-attempts", type=int, default=3, help="Mark recipients failed after this many interrupted/failed attempts.")

    def handle(self, *args, **options):
        once = options["once"]
        sleep = options["sleep"]
        batch_size = options["batch_size"]
        stale_minutes = options["stale_minutes"]
        max_attempts = options["max_attempts"]
        if options["workers"]:
            workers = max(1, options["workers"])
        elif getattr(settings, "IS_TESTING", False):
            workers = 1
        else:
            workers = 1 if connection.vendor == "sqlite" else 4

        while True:
            self.recover_stale_sending(stale_minutes, max_attempts)
            processed = self.process_batch(batch_size, workers)
            if once:
                break
            if not processed:
                time.sleep(sleep)

    def process_batch(self, batch_size, workers=4):
        jobs = list(
            EmailDeliveryJob.objects.filter(status__in=["queued", "sending"])
            .order_by("created_at")[:5]
        )
        if not jobs:
            return 0

        processed = 0
        for job in jobs:
            if job.status == "queued":
                job.status = "sending"
                job.save(update_fields=["status"])

            with transaction.atomic():
                recipient_ids = list(
                    EmailDeliveryRecipient.objects.select_for_update(skip_locked=True)
                    .filter(job=job, status="pending")
                    .order_by("created_at", "id")
                    .values_list("id", flat=True)[:batch_size]
                )
                if recipient_ids:
                    EmailDeliveryRecipient.objects.filter(id__in=recipient_ids, status="pending").update(status="sending")
            if not recipient_ids:
                update_job_after_batch(job)
                continue

            recipients = list(EmailDeliveryRecipient.objects.select_related("job").filter(id__in=recipient_ids))
            if workers == 1:
                for recipient in recipients:
                    process_email_recipient(recipient)
                    processed += 1
            else:
                with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="email-worker") as executor:
                    futures = [executor.submit(process_email_recipient, recipient) for recipient in recipients]
                    for future in as_completed(futures):
                        future.result()
                        processed += 1
            update_job_after_batch(job)

        if processed:
            self.stdout.write(f"Processed {processed} queued email recipient(s).")
        return processed

    def recover_stale_sending(self, stale_minutes, max_attempts):
        cutoff = timezone.now() - timedelta(minutes=stale_minutes)
        stale = EmailDeliveryRecipient.objects.filter(status="sending", created_at__lt=cutoff)
        job_ids = list(stale.values_list("job_id", flat=True).distinct())
        failed = stale.filter(attempts__gte=max_attempts).update(
            status="failed",
            last_error="Email delivery interrupted while sending.",
        )
        retried = stale.filter(attempts__lt=max_attempts).update(status="pending")
        if failed or retried:
            for job in EmailDeliveryJob.objects.filter(id__in=job_ids):
                update_job_after_batch(job)
            self.stdout.write(f"Recovered {retried} stale sending recipient(s); marked {failed} failed.")
