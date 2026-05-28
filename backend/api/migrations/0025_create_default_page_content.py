from django.db import migrations


PAGE_DEFAULTS = {
    "book": {
        "seo_title": "Book a Tour | Dolphin Island Tours",
        "seo_description": "Book a Dolphin Island Tours boat tour.",
        "hero_title": "Book your Dolphin Island Tours trip.",
    },
    "reviews": {
        "seo_title": "Guest Reviews | Dolphin Island Tours",
        "seo_description": "Read verified guest reviews for Dolphin Island Tours across wildlife, sunset, dolphin, and Space Coast boat tours.",
        "hero_title": "Reviews from every tour.",
        "intro_title": "Guest reviews",
    },
    "login": {
        "seo_title": "Login | Dolphin Island Tours",
        "seo_description": "Log in to your Dolphin Island Tours account.",
        "hero_title": "Log in to your account.",
    },
    "signup": {
        "seo_title": "Sign Up | Dolphin Island Tours",
        "seo_description": "Create a Dolphin Island Tours account.",
        "hero_title": "Create your Dolphin Island Tours account.",
    },
    "account": {
        "seo_title": "Account | Dolphin Island Tours",
        "seo_description": "Manage your Dolphin Island Tours account details and marketing email preferences.",
        "hero_title": "Account",
    },
    "bookings": {
        "seo_title": "My Bookings | Dolphin Island Tours",
        "seo_description": "Review your Dolphin Island Tours bookings and receipts.",
        "hero_title": "My bookings",
    },
    "forgot_password": {
        "seo_title": "Forgot Password | Dolphin Island Tours",
        "seo_description": "Request a Dolphin Island Tours password reset link.",
        "hero_title": "Reset your password.",
    },
    "reset_password": {
        "seo_title": "Reset Password | Dolphin Island Tours",
        "seo_description": "Set a new Dolphin Island Tours account password.",
        "hero_title": "Set a new password.",
    },
}


def create_missing_pages(apps, schema_editor):
    PageContent = apps.get_model("api", "PageContent")
    for page, defaults in PAGE_DEFAULTS.items():
        PageContent.objects.get_or_create(page=page, defaults=defaults)


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0024_pagesection_expand_page_choices"),
    ]

    operations = [
        migrations.RunPython(create_missing_pages, migrations.RunPython.noop),
    ]
