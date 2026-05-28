from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0018_remove_sitesettings_tax_rate_percent_and_more"),
    ]

    operations = [
        migrations.DeleteModel(
            name="ActivityLog",
        ),
    ]
