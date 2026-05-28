from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0016_deleted_booking_report"),
    ]

    operations = [
        migrations.AddField(
            model_name="tour",
            name="tax_rate_percent",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text="Optional sales tax percentage for this tour. Leave blank to use Site settings.",
                max_digits=5,
                null=True,
            ),
        ),
    ]
