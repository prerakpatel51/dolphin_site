# Generated manually for per-tour pricing and party-size rules.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0003_pagecontent_site_admin_expansion"),
    ]

    operations = [
        migrations.AddField(
            model_name="tour",
            name="price_per_person",
            field=models.PositiveIntegerField(default=60, help_text="USD per guest."),
        ),
        migrations.AddField(
            model_name="tour",
            name="min_party",
            field=models.PositiveSmallIntegerField(default=3),
        ),
        migrations.AddField(
            model_name="tour",
            name="max_party",
            field=models.PositiveSmallIntegerField(default=6),
        ),
    ]
