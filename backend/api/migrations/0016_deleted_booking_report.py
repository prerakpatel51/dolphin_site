from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0015_visitor_events_and_activity_indexes"),
    ]

    operations = [
        migrations.CreateModel(
            name="DeletedBookingReport",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("booking_id", models.UUIDField(unique=True)),
                ("user_email", models.EmailField(blank=True, max_length=254)),
                ("customer_name", models.CharField(max_length=120)),
                ("customer_email", models.EmailField(max_length=254)),
                ("customer_phone", models.CharField(blank=True, max_length=32)),
                ("tour_name", models.CharField(blank=True, max_length=120)),
                ("tour_date", models.DateField(blank=True, null=True)),
                ("tour_time", models.TimeField(blank=True, null=True)),
                ("party_size", models.PositiveSmallIntegerField()),
                ("status", models.CharField(max_length=16)),
                ("price_per_person_cents", models.PositiveIntegerField()),
                ("discount_cents", models.PositiveIntegerField(default=0)),
                ("tax_cents", models.PositiveIntegerField(default=0)),
                ("total_cents", models.PositiveIntegerField()),
                ("square_payment_id", models.CharField(blank=True, max_length=128)),
                ("square_order_id", models.CharField(blank=True, max_length=128)),
                ("promo_code_text", models.CharField(blank=True, max_length=40)),
                ("travelers", models.JSONField(blank=True, default=list)),
                ("special_requests", models.TextField(blank=True)),
                ("original_created_at", models.DateTimeField()),
                ("original_updated_at", models.DateTimeField()),
                ("deleted_at", models.DateTimeField(auto_now_add=True)),
                ("deleted_by", models.EmailField(blank=True, max_length=254)),
            ],
            options={
                "ordering": ["-original_created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="deletedbookingreport",
            index=models.Index(fields=["-original_created_at"], name="delbook_created_idx"),
        ),
        migrations.AddIndex(
            model_name="deletedbookingreport",
            index=models.Index(fields=["status", "-original_created_at"], name="delbook_status_created_idx"),
        ),
        migrations.AddIndex(
            model_name="deletedbookingreport",
            index=models.Index(fields=["customer_email", "-original_created_at"], name="delbook_email_created_idx"),
        ),
    ]
