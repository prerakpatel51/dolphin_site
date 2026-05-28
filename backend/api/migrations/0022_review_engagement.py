import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0021_activitylog"),
    ]

    operations = [
        migrations.AddField(
            model_name="review",
            name="photo",
            field=models.ImageField(blank=True, null=True, upload_to="reviews/"),
        ),
        migrations.AddField(
            model_name="review",
            name="reply_text",
            field=models.TextField(blank=True, help_text="Public owner reply shown below the review."),
        ),
        migrations.AddField(
            model_name="review",
            name="helpful_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.CreateModel(
            name="ReviewHelpfulVote",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("session_key", models.CharField(blank=True, max_length=40)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("review", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="helpful_votes", to="api.review")),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="review_helpful_votes", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddIndex(
            model_name="reviewhelpfulvote",
            index=models.Index(fields=["review", "user"], name="review_vote_user_idx"),
        ),
        migrations.AddIndex(
            model_name="reviewhelpfulvote",
            index=models.Index(fields=["review", "session_key"], name="review_vote_session_idx"),
        ),
    ]
