from django.db import migrations, models


NEW_EMAIL = "lauren@dolphinislandtours.com"
OLD_EMAILS = {
    "info@dolphinislandtours.com",
    "lewis@dolphinislandtours.com",
}


def update_contact_email(apps, schema_editor):
    SiteSettings = apps.get_model("api", "SiteSettings")
    SiteSettings.objects.filter(contact_email__in=OLD_EMAILS).update(contact_email=NEW_EMAIL)


def restore_contact_email(apps, schema_editor):
    SiteSettings = apps.get_model("api", "SiteSettings")
    SiteSettings.objects.filter(contact_email=NEW_EMAIL).update(contact_email="info@dolphinislandtours.com")


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0029_ratelimit_bucket"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sitesettings",
            name="contact_email",
            field=models.EmailField(default=NEW_EMAIL, max_length=254),
        ),
        migrations.RunPython(update_contact_email, restore_contact_email),
    ]
