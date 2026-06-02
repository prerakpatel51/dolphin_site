from django.db import migrations, models


HEADER_TITLE = "Cruise with Dolphins, Sunsets, Rocket Launches, and Smiles"
TAGLINE = "Creating unforgettable dolphin encounters on Florida's Space Coast."
ADDRESS = "2700 Harbor Town Drive, Merritt Island, FL 32952"
PHONE = "321-390-0176"
EMAIL = "info@dolphinislandtours.com"
LEGAL = "Copyright © 2026 Dolphin Island Tours LLC | Licensed & Insured | USCG Certified Captain"
MAPS_URL = "https://maps.google.com/?q=2700+Harbor+Town+Drive+Merritt+Island+FL+32952"
MAP_EMBED_URL = "https://www.google.com/maps?q=2700+Harbor+Town+Drive+Merritt+Island+FL+32952&output=embed"

ABOUT_BODY = (
    "Welcome to Dolphin Island Tours, where unforgettable memories meet the beauty of Florida's coastline. "
    "Based in Merritt Island, we created our dolphin tour company from a love of the water, wildlife, and "
    "sharing the natural beauty of the Space Coast with others.\n\n"
    "What started as a dream quickly became a mission to give families, couples, and visitors a relaxing "
    "and exciting way to experience dolphins in their natural habitat.\n\n"
    "Our tours are designed to feel personal, welcoming, and authentic. Whether you're spotting playful "
    "dolphins, enjoying a breathtaking sunset, or simply relaxing on the water, we want every guest to "
    "leave with memories they'll never forget.\n\n"
    "We are proud to be locally owned and operated, and we can't wait to welcome you aboard."
)


FOOTER_LINKS = [
    ("Book a Tour", "/tours", 10),
    ("About Us", "/about", 20),
    ("FAQs", "/#faq", 30),
    ("Contact", "/contact", 40),
]


def apply_copy(apps, schema_editor):
    SiteSettings = apps.get_model("api", "SiteSettings")
    PageContent = apps.get_model("api", "PageContent")
    NavigationLink = apps.get_model("api", "NavigationLink")

    settings, _ = SiteSettings.objects.get_or_create(pk=1)
    settings.tagline = TAGLINE
    settings.contact_email = EMAIL
    settings.contact_phone = PHONE
    settings.address = ADDRESS
    settings.maps_url = MAPS_URL
    settings.map_embed_url = MAP_EMBED_URL
    settings.footer_legal_text = LEGAL
    settings.save(update_fields=[
        "tagline", "contact_email", "contact_phone", "address", "maps_url",
        "map_embed_url", "footer_legal_text",
    ])

    PageContent.objects.update_or_create(
        page="home",
        defaults={
            "hero_title": HEADER_TITLE,
            "hero_subtitle": (
                "Small-group Merritt Island boat tours for dolphin watching, sunsets, "
                "rocket launch viewing, and easy days on the water."
            ),
        },
    )
    PageContent.objects.update_or_create(
        page="about",
        defaults={
            "hero_eyebrow": "About us",
            "hero_title": "About Dolphin Island Tours",
            "intro_title": "Welcome aboard.",
            "intro_body": ABOUT_BODY,
            "section_one_title": "Personal, welcoming, and authentic.",
            "section_one_body": (
                "Every trip is built around small groups, local knowledge, and a relaxed Space Coast experience."
            ),
        },
    )

    NavigationLink.objects.filter(area="footer").update(is_active=False)
    for label, url, sort_order in FOOTER_LINKS:
        NavigationLink.objects.update_or_create(
            area="footer",
            label=label,
            defaults={
                "url": url,
                "visibility": "all",
                "is_button": False,
                "opens_new_tab": False,
                "is_active": True,
                "sort_order": sort_order,
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0026_navigationlink"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sitesettings",
            name="tagline",
            field=models.CharField(default=TAGLINE, max_length=240),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="contact_email",
            field=models.EmailField(default=EMAIL, max_length=254),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="contact_phone",
            field=models.CharField(blank=True, default=PHONE, max_length=40),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="address",
            field=models.CharField(default=ADDRESS, max_length=240),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="maps_url",
            field=models.URLField(blank=True, default=MAPS_URL),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="map_embed_url",
            field=models.URLField(blank=True, default=MAP_EMBED_URL),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="footer_legal_text",
            field=models.CharField(
                blank=True,
                default=LEGAL,
                max_length=240,
            ),
        ),
        migrations.RunPython(apply_copy, migrations.RunPython.noop),
    ]
