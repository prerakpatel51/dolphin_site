from django.core.management.base import BaseCommand

from api.management.commands.seed import PAGE_DEFAULTS, TOURS
from api.models import FAQItem, PageContent, SiteSettings, Tour


class Command(BaseCommand):
    help = "Apply optimized SEO titles, descriptions, keywords, and page copy to existing content."

    def handle(self, *args, **opts):
        settings = SiteSettings.get()
        settings.site_name = "Dolphin Island Tours"
        settings.tagline = "Creating unforgettable dolphin encounters on Florida's Space Coast."
        settings.seo_title = "Dolphin Island Tours | Private Merritt Island Boat Tours"
        settings.seo_description = (
            "Book private and small-group Merritt Island dolphin tours, sunset cruises, wildlife "
            "trips, and rocket launch boat tours near Cocoa Beach."
        )
        settings.seo_keywords = (
            "Merritt Island dolphin tours, private boat tour Cocoa Beach, exclusive boat tours, "
            "Cape Canaveral rocket launch boat tour, Indian River Lagoon, sunset cruise, manatee tour"
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

        legacy_tour_count = Tour.objects.filter(slug="rocket-launch").update(
            name="Rocket Launch Viewing",
            short_description="Watch Space Coast rocket launches from the water on a private-style boat tour near Cape Canaveral.",
            long_description=(
                "Watch rocket launches from the Indian River Lagoon with a local Space Coast captain. "
                "This private-style Merritt Island boat tour is close to Cape Canaveral, Cocoa Beach, "
                "Port Canaveral, and Kennedy Space Center, with open-water views and a personal small-group feel."
            ),
            seo_title="Private Rocket Launch Boat Tour | Cape Canaveral",
            seo_description=(
                "Book a private-style rocket launch viewing boat tour near Cape Canaveral, Cocoa Beach, "
                "Kennedy Space Center, and Merritt Island."
            ),
            seo_keywords=(
                "Cape Canaveral rocket launch boat tour, private launch viewing, Space Coast rocket launch, "
                "Cocoa Beach launch tour, Kennedy Space Center boat tour"
            ),
        )

        faqs = [
            (
                "Can we book a private or exclusive boat tour?",
                "Yes. Dolphin Island Tours specializes in small private-style trips for 3 to 6 guests, so your group can enjoy the boat without joining a crowd. Contact us for private tour requests, celebrations, and custom timing.",
            ),
            (
                "Are alcohol, smoking, or special onboard preferences allowed?",
                "Private trips may be able to accommodate personal preferences when the captain, guests, safety rules, and marina policies allow it. Tell us what you have in mind before booking so we can confirm what is possible for your group.",
            ),
            (
                "What wildlife can we see on a Merritt Island boat tour?",
                "Guests often see bottlenose dolphins, manatees, pelicans, ospreys, shorebirds, and other Indian River Lagoon wildlife. Sightings vary by season, weather, tide, and conditions.",
            ),
            (
                "Where do Dolphin Island Tours depart from?",
                "Tours depart from 2700 Harbor Town Drive in Merritt Island, Florida, near Cocoa Beach, Cape Canaveral, Port Canaveral, Kennedy Space Center, and the Florida Space Coast.",
            ),
            (
                "Do you offer sunset cruises near Cocoa Beach?",
                "Yes. We offer small-group and private-style sunset cruises from Merritt Island on the Indian River Lagoon, close to Cocoa Beach, Cape Canaveral, and Port Canaveral.",
            ),
            (
                "Can we watch a rocket launch from the boat?",
                "Launch-day boat tours may be available when schedules, launch windows, weather, and water conditions line up. Contact Dolphin Island Tours before booking if rocket launch viewing is your main goal.",
            ),
        ]
        for index, (question, answer) in enumerate(faqs, start=1):
            FAQItem.objects.update_or_create(
                question=question,
                defaults={"answer": answer, "sort_order": index, "is_active": True},
            )

        self.stdout.write(self.style.SUCCESS(
            f"Applied SEO defaults to site settings, {page_count} pages, {tour_count} tours, {legacy_tour_count} legacy tours, and {len(faqs)} FAQs."
        ))
