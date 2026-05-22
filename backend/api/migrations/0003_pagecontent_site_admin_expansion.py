# Generated manually for editable site content/admin expansion.

import decimal
from django.db import migrations, models
import django.db.models.deletion


SITE_IMAGES = {
    "hero": ("/images/hero-ocean.jpg", "Boat tour on the Space Coast"),
    "tours_hero": ("/images/sunset-water.jpg", "Sunset over the Indian River Lagoon"),
    "contact_hero": ("/images/lagoon.jpg", "Indian River Lagoon"),
    "about": ("/images/boat.jpg", "Dolphin Island Tours boat"),
    "about_secondary": ("/images/welcome.jpg", "Guests at Dolphin Island Tours"),
    "story": ("/images/lagoon.jpg", "Space Coast lagoon"),
    "highlight_dolphin": ("/images/dolphin.jpg", "Wild dolphin"),
    "highlight_manatee": ("/images/manatee.jpg", "Manatee"),
    "highlight_rocket": ("/images/rocket.jpg", "Rocket launch"),
    "gallery_1": ("/images/dolphin.jpg", "Dolphin in the water"),
    "gallery_2": ("/images/sunset.jpg", "Sunset cruise"),
    "gallery_3": ("/images/manatee.jpg", "Manatee in the lagoon"),
    "gallery_4": ("/images/boat.jpg", "Tour boat"),
    "gallery_5": ("/images/sunset-water.jpg", "Sunset over water"),
    "gallery_6": ("/images/lagoon.jpg", "Indian River Lagoon"),
    "gallery_7": ("/images/welcome.jpg", "Welcome aboard"),
    "gallery_8": ("/images/rocket.jpg", "Rocket launch viewing"),
    "og_default": ("/images/hero-ocean.jpg", "Dolphin Island Tours"),
}


PAGE_DEFAULTS = {
    "home": {
        "hero": "hero",
        "seo_title": "Dolphin Island Tours - Space Coast Wildlife & Sunset Cruises",
        "seo_description": "Small-group wildlife and sunset boat tours from Merritt Island, FL. Wild dolphins, manatees, rocket launches. Book online.",
        "seo_keywords": "dolphin tours, merritt island, space coast, sunset cruise, wildlife tour, florida boat tour, rocket launch viewing",
        "hero_eyebrow": "Merritt Island · Space Coast, FL",
        "hero_title": "Explore the wonders of the Space Coast.",
        "hero_subtitle": "Small-group wildlife and sunset boat tours from the heart of the Indian River Lagoon. Wild dolphins, manatees, rocket launches - book in under a minute.",
        "primary_button_label": "Book a tour",
        "primary_button_url": "/tours",
        "secondary_button_label": "What you'll see",
        "secondary_button_url": "#highlights",
        "intro_eyebrow": "What you'll see",
        "intro_title": "More than just a boat ride.",
        "section_one_title": "Two unforgettable tours.",
        "section_one_body": "Small-group wildlife and sunset tours built for families, visitors, and locals.",
        "section_two_title": "500+ five-star trips.",
        "cta_title": "At the Harbortown marina.",
        "cta_body": "Tours leave on time - arrive 15 minutes early.",
    },
    "tours": {
        "hero": "tours_hero",
        "seo_title": "Tours - Dolphin Island Tours",
        "seo_description": "Browse Dolphin Island Tours wildlife excursions and sunset cruises from Merritt Island, FL.",
        "hero_eyebrow": "Pick your trip",
        "hero_title": "Tours",
        "hero_subtitle": "Small groups. Big water. $60 per person - 3 to 6 guests per boat.",
    },
    "about": {
        "hero": "about",
        "seo_title": "About - Dolphin Island Tours",
        "seo_description": "Learn about Dolphin Island Tours, a locally owned Space Coast boat tour company founded in 2010.",
        "hero_eyebrow": "Our story",
        "hero_title": "Locally owned. Quietly run.",
        "intro_body": "Dolphin Island Tours was founded in 2010 with a simple mission: share the wonder of the Space Coast with small groups of curious travelers. We run personal, affordable, eco-conscious boat tours from Merritt Island, Florida.",
        "section_one_title": "Our values",
    },
    "contact": {
        "hero": "contact_hero",
        "seo_title": "Contact - Dolphin Island Tours",
        "seo_description": "Questions about a tour, private charter, or special event? Send Dolphin Island Tours a message.",
        "hero_eyebrow": "Get in touch",
        "hero_title": "Questions? Custom trips?",
        "section_one_title": "Reach us directly",
        "section_one_body": "We reply to every message within one business day.",
        "section_two_title": "Send a message",
        "cta_title": "Thanks - we got it.",
        "cta_body": "Check your inbox for a confirmation. We'll reply within one business day.",
    },
}


def seed_content(apps, schema_editor):
    SiteImage = apps.get_model("api", "SiteImage")
    PageContent = apps.get_model("api", "PageContent")

    image_objects = {}
    for key, (path, alt) in SITE_IMAGES.items():
        obj, _ = SiteImage.objects.get_or_create(key=key, defaults={"default_path": path, "alt_text": alt})
        updates = []
        if not obj.default_path:
            obj.default_path = path
            updates.append("default_path")
        if not obj.alt_text:
            obj.alt_text = alt
            updates.append("alt_text")
        if updates:
            obj.save(update_fields=updates)
        image_objects[key] = obj

    for page, data in PAGE_DEFAULTS.items():
        data = dict(data)
        hero_key = data.pop("hero")
        defaults = dict(data)
        defaults["hero_image"] = image_objects.get(hero_key)
        PageContent.objects.get_or_create(page=page, defaults=defaults)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0002_activitylog_contactmessage_siteimage_sitesettings_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="siteimage",
            name="image",
            field=models.ImageField(blank=True, null=True, upload_to="site/"),
        ),
        migrations.AlterField(
            model_name="siteimage",
            name="key",
            field=models.CharField(
                choices=[
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
        migrations.AddField(
            model_name="siteimage",
            name="default_path",
            field=models.CharField(blank=True, help_text="Fallback static path used until an uploaded replacement exists, e.g. /images/hero-ocean.jpg.", max_length=240),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="average_rating",
            field=models.DecimalField(decimal_places=1, default=decimal.Decimal("5.0"), max_digits=2),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="google_ads_booking_conversion_label",
            field=models.CharField(blank=True, max_length=80),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="google_ads_id",
            field=models.CharField(blank=True, help_text="e.g. AW-123456789", max_length=40),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="google_business_url",
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="google_tag_manager_id",
            field=models.CharField(blank=True, help_text="e.g. GTM-XXXXXXX", max_length=40),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="map_embed_url",
            field=models.URLField(blank=True, default="https://www.google.com/maps?q=2700+Harbortown+Drive+Merritt+Island+FL&output=embed"),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="maps_url",
            field=models.URLField(blank=True, default="https://maps.google.com/?q=2700+Harbortown+Drive+Merritt+Island+FL"),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="meeting_instructions",
            field=models.CharField(blank=True, default="Arrive 15 minutes before departure.", max_length=240),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="meta_pixel_id",
            field=models.CharField(blank=True, max_length=40),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="price_blurb",
            field=models.CharField(blank=True, default="$60 per person · 3–6 guests", max_length=160),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="review_count",
            field=models.PositiveIntegerField(default=500),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="tiktok_url",
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="youtube_url",
            field=models.URLField(blank=True),
        ),
        migrations.CreateModel(
            name="PageContent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("page", models.CharField(choices=[("home", "Home"), ("tours", "Tours listing"), ("about", "About"), ("contact", "Contact")], max_length=32, unique=True)),
                ("seo_title", models.CharField(blank=True, max_length=70)),
                ("seo_description", models.CharField(blank=True, max_length=180)),
                ("seo_keywords", models.CharField(blank=True, max_length=240)),
                ("hero_eyebrow", models.CharField(blank=True, max_length=120)),
                ("hero_title", models.CharField(blank=True, max_length=180)),
                ("hero_subtitle", models.TextField(blank=True)),
                ("primary_button_label", models.CharField(blank=True, max_length=80)),
                ("primary_button_url", models.CharField(blank=True, max_length=200)),
                ("secondary_button_label", models.CharField(blank=True, max_length=80)),
                ("secondary_button_url", models.CharField(blank=True, max_length=200)),
                ("intro_eyebrow", models.CharField(blank=True, max_length=120)),
                ("intro_title", models.CharField(blank=True, max_length=180)),
                ("intro_body", models.TextField(blank=True)),
                ("section_one_title", models.CharField(blank=True, max_length=180)),
                ("section_one_body", models.TextField(blank=True)),
                ("section_two_title", models.CharField(blank=True, max_length=180)),
                ("section_two_body", models.TextField(blank=True)),
                ("cta_title", models.CharField(blank=True, max_length=180)),
                ("cta_body", models.TextField(blank=True)),
                ("extra_content", models.JSONField(blank=True, default=dict, help_text="Optional structured content for cards/FAQs/testimonials. Leave as {} if not needed.")),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("hero_image", models.ForeignKey(blank=True, help_text="Optional hero image slot. Upload/replace the image under Site images.", null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="pages", to="api.siteimage")),
            ],
            options={
                "verbose_name": "Page content",
                "verbose_name_plural": "Page content",
                "ordering": ["page"],
            },
        ),
        migrations.RunPython(seed_content, noop),
    ]
