from django.db import migrations, models


GOOGLE_BUSINESS_URL = "https://share.google/Ig5FtVIQGXBWMUIGC"
GOOGLE_REVIEW_URL = "https://g.page/r/CehBxKNRm1TfEBM/review"
GOOGLE_REVIEWS_URL = "https://share.google/Ig5FtVIQGXBWMUIGC"
GOOGLE_REVIEWS_EMBED_URL = (
    "https://www.google.com/maps?q="
    "Dolphin+Island+Tours+LLC+2700+Harbortown+Dr+Merritt+Island+FL+32952&output=embed"
)

SITE_SEO_DESCRIPTION = (
    "Dolphin Island Tours LLC offers private and small-group boat tours from Merritt Island, Florida, near "
    "Cocoa Beach, Cape Canaveral, Port Canaveral, Kennedy Space Center, and the Indian River Lagoon. Guests "
    "can book dolphin watching trips, manatee and wildlife tours, sunset cruises, rocket launch viewing trips, "
    "family boat tours, couples cruises, custom private charters, and relaxed Space Coast sightseeing on the "
    "water. Tours are designed for personal service, local wildlife viewing, calm lagoon scenery, memorable "
    "photos, and easy access from Cocoa Beach, Orlando day trips, cruise port visits, beach vacations, and "
    "Brevard County stays."
)
SITE_SEO_KEYWORDS = (
    "Dolphin Island Tours, Dolphin Island Tours LLC, Merritt Island dolphin tours, Cocoa Beach dolphin tour, "
    "private dolphin tour Merritt Island, small group boat tour Merritt Island, Space Coast boat tours, "
    "Cape Canaveral boat tour, Port Canaveral boat tour, Kennedy Space Center boat tour, Indian River Lagoon "
    "tour, Florida dolphin watching, manatee tour Merritt Island, wildlife boat tour Cocoa Beach, sunset cruise "
    "Merritt Island, private sunset cruise Cocoa Beach, rocket launch boat tour Cape Canaveral, rocket launch "
    "viewing boat, family boat tour Florida, couples boat tour Cocoa Beach, private charter Merritt Island, "
    "Brevard County boat tour, Harbortown Marina tour, Florida eco tour, lagoon wildlife tour"
)

HOME_SEO_DESCRIPTION = (
    "Book a private or small-group Merritt Island dolphin tour with Dolphin Island Tours LLC near Cocoa Beach, "
    "Cape Canaveral, Port Canaveral, Kennedy Space Center, and the Indian River Lagoon. Choose dolphin watching, "
    "manatee and wildlife viewing, sunset cruises, rocket launch viewing, family sightseeing, couples trips, and "
    "custom Space Coast boat tours from Harbortown Marina."
)
HOME_SEO_KEYWORDS = (
    "private Merritt Island dolphin tours, Cocoa Beach boat tours, Dolphin Island Tours LLC, dolphin watching "
    "Merritt Island, Indian River Lagoon wildlife tour, manatee tour Cocoa Beach, sunset cruise Merritt Island, "
    "rocket launch boat tour, Cape Canaveral sightseeing, Port Canaveral shore excursion, Kennedy Space Center "
    "launch viewing, Space Coast private boat tour"
)
REVIEWS_SEO_DESCRIPTION = (
    "Read Google reviews for Dolphin Island Tours LLC and share your own public Google review after a Merritt "
    "Island dolphin tour, sunset cruise, wildlife trip, rocket launch viewing tour, or private Space Coast boat "
    "tour near Cocoa Beach and Cape Canaveral."
)
REVIEWS_SEO_KEYWORDS = (
    "Dolphin Island Tours reviews, Dolphin Island Tours LLC Google reviews, Merritt Island dolphin tour reviews, "
    "Cocoa Beach boat tour reviews, Space Coast boat tour reviews, Cape Canaveral tour reviews, private dolphin "
    "tour reviews"
)


def apply_google_reviews_and_seo(apps, schema_editor):
    SiteSettings = apps.get_model("api", "SiteSettings")
    PageContent = apps.get_model("api", "PageContent")

    settings, _ = SiteSettings.objects.get_or_create(pk=1)
    settings.seo_description = SITE_SEO_DESCRIPTION
    settings.seo_keywords = SITE_SEO_KEYWORDS
    settings.review_count = 1
    settings.average_rating = "5.0"
    settings.google_business_url = settings.google_business_url or GOOGLE_BUSINESS_URL
    settings.google_review_url = GOOGLE_REVIEW_URL
    settings.google_reviews_url = GOOGLE_REVIEWS_URL
    settings.google_reviews_embed_url = GOOGLE_REVIEWS_EMBED_URL
    settings.save()

    PageContent.objects.update_or_create(
        page="home",
        defaults={
            "seo_description": HOME_SEO_DESCRIPTION,
            "seo_keywords": HOME_SEO_KEYWORDS,
            "section_two_title": "Google reviews.",
        },
    )
    PageContent.objects.update_or_create(
        page="reviews",
        defaults={
            "seo_title": "Dolphin Island Tours Google Reviews | Merritt Island",
            "seo_description": REVIEWS_SEO_DESCRIPTION,
            "seo_keywords": REVIEWS_SEO_KEYWORDS,
            "hero_title": "Dolphin Island Tours Google reviews.",
            "intro_title": "Google reviews",
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0030_update_contact_email"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tour",
            name="seo_description",
            field=models.TextField(blank=True, help_text="Search description. Supports long copy up to about 2000 words."),
        ),
        migrations.AlterField(
            model_name="tour",
            name="seo_keywords",
            field=models.TextField(blank=True, help_text="Comma-separated keywords. Supports long lists up to about 2000 words."),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="seo_description",
            field=models.TextField(default="Book small-group dolphin, manatee, wildlife, sunset, and rocket launch boat tours from Merritt Island near Cocoa Beach and Cape Canaveral."),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="seo_keywords",
            field=models.TextField(default="Merritt Island dolphin tours, Cocoa Beach dolphin tour, Cape Canaveral boat tour, Space Coast wildlife tour, Indian River Lagoon tour, Florida sunset cruise"),
        ),
        migrations.AlterField(
            model_name="pagecontent",
            name="seo_description",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="pagecontent",
            name="seo_keywords",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="google_review_url",
            field=models.URLField(blank=True, default=GOOGLE_REVIEW_URL, help_text="Direct Google review/write-review link. Paste the Business Profile review link here if available.", max_length=500),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="google_reviews_url",
            field=models.URLField(blank=True, default=GOOGLE_REVIEWS_URL, help_text="Public Google reviews link.", max_length=500),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="google_reviews_embed_url",
            field=models.URLField(blank=True, default=GOOGLE_REVIEWS_EMBED_URL, help_text="Embeddable Google Maps/Business Profile URL shown on the reviews page.", max_length=500),
        ),
        migrations.RunPython(apply_google_reviews_and_seo, migrations.RunPython.noop),
    ]
