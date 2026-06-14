from django.core.management.base import BaseCommand

from api.views import expire_pending_holds


class Command(BaseCommand):
    help = "Expire pending booking holds older than PENDING_BOOKING_EXPIRY_MINUTES."

    def handle(self, *args, **opts):
        expired = expire_pending_holds()
        self.stdout.write(self.style.SUCCESS(f"Expired {expired} pending booking hold(s)."))
