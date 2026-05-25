import time

from django.core.management.base import BaseCommand

from api.email_queue import process_email_recipient, update_job_after_batch
from api.models import EmailDeliveryJob, EmailDeliveryRecipient


class Command(BaseCommand):
    help = "Process queued email delivery jobs."

    def add_arguments(self, parser):
        parser.add_argument("--once", action="store_true", help="Process available work once and exit.")
        parser.add_argument("--sleep", type=float, default=5.0, help="Seconds to wait between polling attempts.")
        parser.add_argument("--batch-size", type=int, default=25, help="Maximum recipients to send per polling cycle.")

    def handle(self, *args, **options):
        once = options["once"]
        sleep = options["sleep"]
        batch_size = options["batch_size"]

        while True:
            processed = self.process_batch(batch_size)
            if once:
                break
            if not processed:
                time.sleep(sleep)

    def process_batch(self, batch_size):
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

            recipient_ids = list(
                EmailDeliveryRecipient.objects.filter(job=job, status="pending")
                .order_by("created_at", "id")
                .values_list("id", flat=True)[:batch_size]
            )
            if not recipient_ids:
                update_job_after_batch(job)
                continue

            for recipient_id in recipient_ids:
                recipient = EmailDeliveryRecipient.objects.get(pk=recipient_id)
                if recipient.status != "pending":
                    continue
                process_email_recipient(recipient)
                processed += 1
            update_job_after_batch(job)

        if processed:
            self.stdout.write(f"Processed {processed} queued email recipient(s).")
        return processed
