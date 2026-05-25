from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0012_booking_payment_failed_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="booking",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending Payment"),
                    ("paid", "Paid"),
                    ("payment_failed", "Payment Failed"),
                    ("expired", "Expired Hold"),
                    ("cancelled", "Cancelled"),
                    ("refunded", "Refunded"),
                ],
                default="pending",
                max_length=16,
            ),
        ),
    ]
