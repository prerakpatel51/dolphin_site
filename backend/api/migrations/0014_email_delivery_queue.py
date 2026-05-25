from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0013_booking_expired_status"),
    ]

    operations = [
        migrations.CreateModel(
            name="EmailDeliveryJob",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("source", models.CharField(blank=True, max_length=80)),
                ("status", models.CharField(choices=[("queued", "Queued"), ("sending", "Sending"), ("sent", "Sent"), ("failed", "Failed")], default="queued", max_length=10)),
                ("total_count", models.PositiveIntegerField(default=0)),
                ("sent_count", models.PositiveIntegerField(default=0)),
                ("failed_count", models.PositiveIntegerField(default=0)),
                ("created_by", models.EmailField(blank=True, max_length=254)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
                ("campaign", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="delivery_jobs", to="api.emailcampaign")),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="EmailDeliveryRecipient",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("email", models.EmailField(max_length=254)),
                ("subject", models.CharField(max_length=200)),
                ("html", models.TextField()),
                ("status", models.CharField(choices=[("pending", "Pending"), ("sending", "Sending"), ("sent", "Sent"), ("failed", "Failed")], default="pending", max_length=10)),
                ("attempts", models.PositiveSmallIntegerField(default=0)),
                ("last_error", models.TextField(blank=True)),
                ("sent_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("job", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="recipients", to="api.emaildeliveryjob")),
                ("promo_code", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="api.promocode")),
            ],
            options={
                "ordering": ["created_at", "id"],
            },
        ),
        migrations.AddIndex(
            model_name="emaildeliveryjob",
            index=models.Index(fields=["status", "created_at"], name="emailjob_status_created_idx"),
        ),
        migrations.AddIndex(
            model_name="emaildeliveryjob",
            index=models.Index(fields=["campaign", "-created_at"], name="emailjob_campaign_idx"),
        ),
        migrations.AddIndex(
            model_name="emaildeliveryrecipient",
            index=models.Index(fields=["status", "created_at"], name="emailrecip_status_created_idx"),
        ),
        migrations.AddIndex(
            model_name="emaildeliveryrecipient",
            index=models.Index(fields=["job", "status"], name="emailrecip_job_status_idx"),
        ),
        migrations.AddIndex(
            model_name="emaildeliveryrecipient",
            index=models.Index(fields=["email"], name="emailrecip_email_idx"),
        ),
    ]
