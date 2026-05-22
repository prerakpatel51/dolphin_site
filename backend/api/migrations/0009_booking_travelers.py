from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0008_update_seo_defaults"),
    ]

    operations = [
        migrations.AddField(
            model_name="booking",
            name="travelers",
            field=models.JSONField(blank=True, default=list),
        ),
    ]
