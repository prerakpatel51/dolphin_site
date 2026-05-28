from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from api.models import Booking


class Command(BaseCommand):
    help = "Expire pending booking holds older than PENDING_BOOKING_EXPIRY_MINUTES."

    def handle(self, *args, **opts):
        minutes = max(1, int(getattr(settings, "PENDING_BOOKING_EXPIRY_MINUTES", 15)))
        cutoff = timezone.now() - timedelta(minutes=minutes)
        expired = Booking.objects.filter(status="pending", updated_at__lt=cutoff).update(status="expired")
        self.stdout.write(self.style.SUCCESS(f"Expired {expired} pending booking hold(s)."))
