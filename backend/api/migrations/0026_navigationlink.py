from django.db import migrations, models


DEFAULT_LINKS = [
    ("header", "Tours", "/tours", "all", False, 10),
    ("header", "Reviews", "/reviews", "all", False, 20),
    ("header", "About", "/about", "all", False, 30),
    ("header", "Contact", "/contact", "all", False, 40),
    ("header", "My Bookings", "/bookings", "authenticated", False, 50),
    ("header", "Account", "/account", "authenticated", False, 60),
    ("header", "Login", "/login", "anonymous", False, 70),
    ("header", "Sign up", "/signup", "anonymous", True, 80),
    ("footer", "Tours", "/tours", "all", False, 10),
    ("footer", "Reviews", "/reviews", "all", False, 20),
    ("footer", "About", "/about", "all", False, 30),
    ("footer", "Contact", "/contact", "all", False, 40),
    ("footer", "My Bookings", "/bookings", "authenticated", False, 50),
    ("footer", "Account", "/account", "authenticated", False, 60),
]


def seed_navigation(apps, schema_editor):
    NavigationLink = apps.get_model("api", "NavigationLink")
    for area, label, url, visibility, is_button, sort_order in DEFAULT_LINKS:
        NavigationLink.objects.get_or_create(
            area=area,
            label=label,
            url=url,
            defaults={
                "visibility": visibility,
                "is_button": is_button,
                "sort_order": sort_order,
                "is_active": True,
            },
        )


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0025_create_default_page_content"),
    ]

    operations = [
        migrations.CreateModel(
            name="NavigationLink",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("area", models.CharField(choices=[("header", "Header"), ("footer", "Footer")], default="header", max_length=12)),
                ("label", models.CharField(max_length=80)),
                ("url", models.CharField(max_length=200)),
                ("visibility", models.CharField(choices=[("all", "Everyone"), ("anonymous", "Logged-out users"), ("authenticated", "Logged-in users")], default="all", max_length=16)),
                ("is_button", models.BooleanField(default=False, help_text="Use primary button styling in the header.")),
                ("opens_new_tab", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("sort_order", models.PositiveSmallIntegerField(default=0)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["area", "sort_order", "id"],
            },
        ),
        migrations.AddIndex(
            model_name="navigationlink",
            index=models.Index(fields=["area", "is_active", "sort_order"], name="navlink_area_active_idx"),
        ),
        migrations.RunPython(seed_navigation, migrations.RunPython.noop),
    ]
