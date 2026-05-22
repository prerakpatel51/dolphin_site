from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0009_booking_travelers"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="tax_rate_percent",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text="Sales tax percentage added at checkout. Example: 7.00 for 7%.",
                max_digits=5,
            ),
        ),
        migrations.AddField(
            model_name="booking",
            name="tax_cents",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
