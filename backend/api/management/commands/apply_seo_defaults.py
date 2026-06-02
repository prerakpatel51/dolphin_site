from django.core.management.base import BaseCommand

from api.management.commands.seed import PAGE_DEFAULTS, TOURS
from api.models import PageContent, SiteSettings, Tour


class Command(BaseCommand):
    help = "Apply optimized SEO titles, descriptions, keywords, and page copy to existing content."

    def handle(self, *args, **opts):
        settings = SiteSettings.get()
        settings.site_name = "Dolphin Island Tours"
        settings.tagline = "Creating unforgettable dolphin encounters on Florida's Space Coast."
        settings.seo_title = "Dolphin Island Tours | Merritt Island Dolphin & Sunset Boat Tours"
        settings.seo_description = (
            "Book small-group dolphin, manatee, wildlife, sunset, and rocket launch boat tours "
            "from Merritt Island near Cocoa Beach and Cape Canaveral."
        )
        settings.seo_keywords = (
            "Merritt Island dolphin tours, Cocoa Beach dolphin tour, Cape Canaveral boat tour, "
            "Space Coast wildlife tour, Indian River Lagoon tour, Florida sunset cruise"
        )
        settings.robots_txt = (
            "User-agent: *\n"
            "Allow: /\n"
            "Disallow: /admin/\n"
            "Disallow: /api/auth/\n"
            "Disallow: /api/bookings/\n"
            "Sitemap: /sitemap.xml"
        )
        settings.save()

        page_count = 0
        for page, defaults in PAGE_DEFAULTS.items():
            defaults = dict(defaults)
            defaults.pop("hero", None)
            PageContent.objects.update_or_create(page=page, defaults=defaults)
            page_count += 1

        tour_count = 0
        for tour_defaults in TOURS:
            Tour.objects.update_or_create(slug=tour_defaults["slug"], defaults=tour_defaults)
            tour_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Applied SEO defaults to site settings, {page_count} pages, and {tour_count} tours."
        ))
