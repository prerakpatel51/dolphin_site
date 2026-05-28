from django.db import transaction
from django.utils import timezone
import logging

from .emails import campaign_email_html, promotional_email_html, send_email
from .models import EmailDeliveryJob, EmailDeliveryRecipient, PromoCode


logger = logging.getLogger(__name__)


def enqueue_bulk_promotional_email(
    *,
    subject,
    message,
    recipients,
    source_label,
    actor_email="",
    cta_label="",
    cta_url="",
    attach_promo=False,
    promo_kind="percent",
    promo_percent_off=10,
    promo_amount_off_cents=0,
    promo_expires_at=None,
    code_factory=None,
):
    code_factory = code_factory or (lambda prefix: prefix)
    with transaction.atomic():
        job = EmailDeliveryJob.objects.create(
            name=subject,
            source=f"bulk:{source_label}",
            status="queued",
            total_count=len(recipients),
            created_by=actor_email,
        )
        rows = []
        promo_by_email = {}
        if attach_promo:
            promo_objects = []
            for email in recipients:
                promo = PromoCode(
                    code=code_factory("PROMO"),
                    label=f"Bulk email · {subject[:60]}",
                    kind=promo_kind or "percent",
                    percent_off=promo_percent_off or 10,
                    amount_off_cents=promo_amount_off_cents or 0,
                    max_uses=1,
                    locked_to_email=email,
                    expires_at=promo_expires_at,
                )
                promo_objects.append(promo)
                promo_by_email[email] = promo
            PromoCode.objects.bulk_create(promo_objects, batch_size=1000)

        for email in recipients:
            promo = promo_by_email.get(email)
            promo_code = ""
            if promo:
                promo_code = promo.code
            html = (
                campaign_email_html(message, name="", promo_code=promo_code, cta_label=cta_label, cta_url=cta_url)
                if attach_promo
                else promotional_email_html(message, cta_label, cta_url)
            )
            rows.append(EmailDeliveryRecipient(
                job=job,
                email=email,
                subject=subject,
                html=html,
                promo_code=promo,
            ))
        EmailDeliveryRecipient.objects.bulk_create(rows)
    return job


def enqueue_campaign_email(campaign, *, recipients, actor_email="", code_factory=None):
    code_factory = code_factory or (lambda prefix: prefix)
    with transaction.atomic():
        job = EmailDeliveryJob.objects.create(
            name=campaign.subject,
            source="campaign",
            campaign=campaign,
            status="queued",
            total_count=len(recipients),
            created_by=actor_email,
        )
        rows = []
        promo_by_email = {}
        if campaign.attach_promo:
            promo_objects = []
            for email, _name in recipients:
                promo = PromoCode(
                    code=code_factory(f"DI{campaign.pk}"),
                    label=f"Campaign #{campaign.pk} · {campaign.name}",
                    kind=campaign.promo_kind,
                    percent_off=campaign.promo_percent_off,
                    amount_off_cents=campaign.promo_amount_off_cents,
                    max_uses=1,
                    locked_to_email=email,
                    expires_at=campaign.promo_expires_at,
                    campaign=campaign,
                )
                promo_objects.append(promo)
                promo_by_email[email] = promo
            PromoCode.objects.bulk_create(promo_objects, batch_size=1000)

        for email, name in recipients:
            promo = promo_by_email.get(email)
            promo_code = ""
            if promo:
                promo_code = promo.code
            rows.append(EmailDeliveryRecipient(
                job=job,
                email=email,
                subject=campaign.subject,
                html=campaign_email_html(
                    campaign.body,
                    name=name,
                    promo_code=promo_code,
                    cta_label=campaign.cta_label,
                    cta_url=campaign.cta_url,
                    subject_line="",
                ),
                promo_code=promo,
            ))
        EmailDeliveryRecipient.objects.bulk_create(rows)
        campaign.status = "sending"
        campaign.sent_count = 0
        campaign.failed_count = 0
        campaign.last_run_at = timezone.now()
        campaign.save(update_fields=["status", "sent_count", "failed_count", "last_run_at"])
    return job


def process_email_recipient(recipient):
    recipient.status = "sending"
    recipient.attempts += 1
    recipient.save(update_fields=["status", "attempts"])
    try:
        send_email(recipient.email, recipient.subject, recipient.html)
    except Exception as exc:
        logger.exception("Email delivery failed for recipient %s in job %s.", recipient.email, recipient.job_id)
        recipient.status = "failed"
        recipient.last_error = str(exc)
        recipient.save(update_fields=["status", "last_error"])
        return False

    recipient.status = "sent"
    recipient.sent_at = timezone.now()
    recipient.last_error = ""
    recipient.save(update_fields=["status", "sent_at", "last_error"])
    logger.info("Email delivery succeeded for recipient %s in job %s.", recipient.email, recipient.job_id)
    return True


def update_job_after_batch(job):
    job.refresh_from_db()
    if not job.started_at:
        job.started_at = timezone.now()
    job.refresh_stats(save=False)
    update_fields = ["started_at", "total_count", "sent_count", "failed_count", "status", "finished_at"]
    job.save(update_fields=update_fields)
    if job.campaign_id and job.status in ("sent", "failed"):
        campaign = job.campaign
        campaign.status = job.status
        campaign.sent_count = job.sent_count
        campaign.failed_count = job.failed_count
        campaign.last_run_at = job.finished_at or timezone.now()
        campaign.save(update_fields=["status", "sent_count", "failed_count", "last_run_at"])
    return job
