from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string

from api import models


SUPERUSER = {
    "email": "prerakbackup2023@gmail.com",
    "username": "prerakbackup2023@gmail.com",
    "first_name": "Prerak",
    "last_name": "Patel",
    "phone": "3215550100",
}

ADMINS = [
    {
        "email": "patel.prerak2002@gmail.com",
        "username": "patel.prerak2002@gmail.com",
        "first_name": "Lewis",
        "last_name": "Patel",
        "phone": "3215550101",
    },
    {
        "email": "ppatel2025@my.fit.edu",
        "username": "ppatel2025@my.fit.edu",
        "first_name": "Ressis",
        "last_name": "Admin",
        "phone": "3215550102",
    },
]

REGULAR_USERS = [
    {
        "email": "user1@example.com",
        "username": "user1@example.com",
        "first_name": "User",
        "last_name": "One",
        "phone": "3215550103",
    },
    {
        "email": "user2@example.com",
        "username": "user2@example.com",
        "first_name": "User",
        "last_name": "Two",
        "phone": "3215550104",
    },
    {
        "email": "user3@example.com",
        "username": "user3@example.com",
        "first_name": "User",
        "last_name": "Three",
        "phone": "3215550105",
    },
]


class Command(BaseCommand):
    help = "Delete existing users and create the site owner, client admins, and starter users."

    def add_arguments(self, parser):
        parser.add_argument(
            "--yes",
            action="store_true",
            help="Confirm deleting every existing user account first.",
        )

    def handle(self, *args, **options):
        if not options["yes"]:
            raise SystemExit("This command deletes all users. Re-run with --yes to confirm.")

        User = get_user_model()
        deleted_count, _ = User.objects.all().delete()
        admin_group = self.ensure_admin_group()

        owner = self.create_user(User, SUPERUSER, is_staff=True, is_superuser=True)
        admins = [
            self.create_user(User, data, is_staff=True, is_superuser=False, groups=[admin_group])
            for data in ADMINS
        ]
        users = [self.create_user(User, data, is_staff=False, is_superuser=False) for data in REGULAR_USERS]

        self.stdout.write(self.style.WARNING(f"Deleted existing users/related rows: {deleted_count}"))
        self.stdout.write(self.style.SUCCESS("Created account access:"))
        self.print_account("SUPERUSER", owner, owner._plain_password)
        for admin_user in admins:
            self.print_account("ADMIN", admin_user, admin_user._plain_password)
        for regular_user in users:
            self.print_account("USER", regular_user, regular_user._plain_password)

    def ensure_admin_group(self):
        group, _ = Group.objects.get_or_create(name="Client Admin")
        managed_models = [
            models.ActivityLog,
            models.Booking,
            models.ContactMessage,
            models.EmailCampaign,
            models.MailingListEntry,
            models.PageContent,
            models.PromoCode,
            models.Review,
            models.SiteImage,
            models.SiteSettings,
            models.Tour,
            models.TourSlot,
            models.User,
        ]
        permissions = []
        for model in managed_models:
            content_type = ContentType.objects.get_for_model(model)
            permissions.extend(Permission.objects.filter(content_type=content_type))
        group.permissions.set(permissions)
        return group

    def create_user(self, User, data, is_staff, is_superuser, groups=None):
        user = User.objects.create(
            email=data["email"],
            username=data["username"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            phone=data["phone"],
            is_staff=is_staff,
            is_superuser=is_superuser,
            is_active=True,
        )
        password = get_random_string(18)
        user.set_password(password)
        user.save()
        user._plain_password = password
        if groups:
            user.groups.set(groups)
        return user

    def print_account(self, role, user, password):
        self.stdout.write(
            f"{role}: {user.get_full_name() or user.username} | {user.email} | password: {password}"
        )
