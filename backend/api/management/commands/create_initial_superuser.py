import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create or update the initial superuser from environment variables."

    REQUIRED_ENV_VARS = [
        "DJANGO_SUPERUSER_EMAIL",
        "DJANGO_SUPERUSER_PASSWORD",
        "DJANGO_SUPERUSER_FIRST_NAME",
        "DJANGO_SUPERUSER_LAST_NAME",
        "DJANGO_SUPERUSER_PHONE",
    ]

    def handle(self, *args, **options):
        missing = [name for name in self.REQUIRED_ENV_VARS if not os.getenv(name, "").strip()]
        if missing:
            raise CommandError(
                "Missing required environment variables: " + ", ".join(missing)
            )

        email = os.environ["DJANGO_SUPERUSER_EMAIL"].strip().lower()
        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "").strip() or email
        password = os.environ["DJANGO_SUPERUSER_PASSWORD"]
        first_name = os.environ["DJANGO_SUPERUSER_FIRST_NAME"].strip()
        last_name = os.environ["DJANGO_SUPERUSER_LAST_NAME"].strip()
        phone = os.environ["DJANGO_SUPERUSER_PHONE"].strip()

        User = get_user_model()
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "phone": phone,
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )

        changed_fields = []
        desired_values = {
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "is_staff": True,
            "is_superuser": True,
            "is_active": True,
        }
        for field, value in desired_values.items():
            if getattr(user, field) != value:
                setattr(user, field, value)
                changed_fields.append(field)

        user.set_password(password)
        changed_fields.append("password")
        user.save()

        action = "Created" if created else "Updated"
        self.stdout.write(
            self.style.SUCCESS(
                f"{action} superuser {email}."
            )
        )
        if changed_fields:
            self.stdout.write("Fields set: " + ", ".join(changed_fields))
