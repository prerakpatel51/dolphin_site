import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0023_reviewphoto"),
    ]

    operations = [
        migrations.AlterField(
            model_name="siteimage",
            name="key",
            field=models.CharField(
                choices=[
                    ("logo", "Logo"),
                    ("hero", "Homepage hero"),
                    ("tours_hero", "Tours page hero"),
                    ("contact_hero", "Contact page hero"),
                    ("about", "About page banner"),
                    ("about_secondary", "About secondary image"),
                    ("story", "Story section background"),
                    ("highlight_dolphin", "Highlight: dolphins"),
                    ("highlight_manatee", "Highlight: manatees"),
                    ("highlight_rocket", "Highlight: rocket"),
                    ("gallery_1", "Gallery 1"),
                    ("gallery_2", "Gallery 2"),
                    ("gallery_3", "Gallery 3"),
                    ("gallery_4", "Gallery 4"),
                    ("gallery_5", "Gallery 5"),
                    ("gallery_6", "Gallery 6"),
                    ("gallery_7", "Gallery 7"),
                    ("gallery_8", "Gallery 8"),
                    ("og_default", "Default social share image"),
                ],
                max_length=40,
                unique=True,
            ),
        ),
        migrations.AlterField(
            model_name="pagecontent",
            name="page",
            field=models.CharField(
                choices=[
                    ("home", "Home"),
                    ("tours", "Tours listing"),
                    ("book", "Booking"),
                    ("reviews", "Reviews"),
                    ("about", "About"),
                    ("contact", "Contact"),
                    ("login", "Login"),
                    ("signup", "Sign up"),
                    ("account", "Account"),
                    ("bookings", "My bookings"),
                    ("forgot_password", "Forgot password"),
                    ("reset_password", "Reset password"),
                ],
                max_length=32,
                unique=True,
            ),
        ),
        migrations.CreateModel(
            name="PageSection",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=160)),
                ("eyebrow", models.CharField(blank=True, max_length=80)),
                ("body", models.TextField(blank=True)),
                ("background_color", models.CharField(blank=True, help_text="Optional CSS color, e.g. #fff7ed. Leave blank to use the selected style.", max_length=32)),
                ("text_color", models.CharField(blank=True, help_text="Optional CSS color, e.g. #0b3a52. Leave blank to use the selected style.", max_length=32)),
                ("style", models.CharField(choices=[("light", "Light"), ("ocean", "Ocean"), ("sunset", "Sunset / sale"), ("dark", "Dark")], default="light", max_length=12)),
                ("cta_label", models.CharField(blank=True, max_length=80)),
                ("cta_url", models.CharField(blank=True, max_length=200)),
                ("is_active", models.BooleanField(default=True)),
                ("sort_order", models.PositiveSmallIntegerField(default=0)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("image", models.ForeignKey(blank=True, help_text="Optional image shown beside the content.", null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="page_sections", to="api.siteimage")),
                ("page_content", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="sections", to="api.pagecontent")),
            ],
            options={
                "ordering": ["sort_order", "id"],
            },
        ),
        migrations.AddIndex(
            model_name="pagesection",
            index=models.Index(fields=["page_content", "is_active", "sort_order"], name="pagesection_page_active_idx"),
        ),
    ]
