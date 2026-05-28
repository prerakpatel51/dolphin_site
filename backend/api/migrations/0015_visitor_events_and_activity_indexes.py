from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("api", "0014_email_delivery_queue"),
    ]

    operations = [
        migrations.CreateModel(
            name="VisitorEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("event_type", models.CharField(choices=[("page_view", "Page view"), ("booking_purchase", "Booking purchase")], default="page_view", max_length=40)),
                ("visitor_id", models.CharField(db_index=True, max_length=80)),
                ("path", models.CharField(max_length=500)),
                ("page_title", models.CharField(blank=True, max_length=240)),
                ("referrer", models.CharField(blank=True, max_length=500)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.TextField(blank=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="visitor_events", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="activitylog",
            index=models.Index(fields=["-created_at"], name="activity_created_idx"),
        ),
        migrations.AddIndex(
            model_name="activitylog",
            index=models.Index(fields=["level", "-created_at"], name="activity_level_created_idx"),
        ),
        migrations.AddIndex(
            model_name="activitylog",
            index=models.Index(fields=["action", "-created_at"], name="activity_action_created_idx"),
        ),
        migrations.AddIndex(
            model_name="activitylog",
            index=models.Index(fields=["actor", "-created_at"], name="activity_actor_created_idx"),
        ),
        migrations.AddIndex(
            model_name="visitorevent",
            index=models.Index(fields=["event_type", "-created_at"], name="visit_event_created_idx"),
        ),
        migrations.AddIndex(
            model_name="visitorevent",
            index=models.Index(fields=["visitor_id", "-created_at"], name="visit_visitor_created_idx"),
        ),
        migrations.AddIndex(
            model_name="visitorevent",
            index=models.Index(fields=["user", "-created_at"], name="visit_user_created_idx"),
        ),
        migrations.AddIndex(
            model_name="visitorevent",
            index=models.Index(fields=["path", "-created_at"], name="visit_path_created_idx"),
        ),
    ]
