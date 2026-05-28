from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, time
from api.models import Tour, TourSlot, SiteImage, PageContent


TOURS = [
    {
        "slug": "dolphin-wildlife-excursion",
        "name": "Dolphin Wildlife Excursion",
        "short_description": "Spot wild dolphins, manatees, pelicans, and shorebirds on a Merritt Island wildlife tour near Cocoa Beach.",
        "long_description": (
            "Cruise the protected Indian River Lagoon around Merritt Island looking for wild bottlenose "
            "dolphins, manatees, ospreys, pelicans, and shorebirds. This small-group Space Coast wildlife "
            "tour is close to Cocoa Beach, Cape Canaveral, and Port Canaveral, with local stories about "
            "lagoon ecology, rockets, and coastal Florida history."
        ),
        "duration_minutes": 120,
        "price_per_person": 60,
        "min_party": 3,
        "max_party": 6,
        "image_url": "/images/dolphin.jpg",
        "sort_order": 1,
        "seo_title": "Dolphin Wildlife Excursion | Merritt Island Dolphin & Manatee Tour",
        "seo_description": "Book a Merritt Island dolphin and manatee wildlife tour near Cocoa Beach. Explore the Indian River Lagoon with a local Space Coast captain.",
        "seo_keywords": "Merritt Island dolphin tour, Cocoa Beach dolphin tour, manatee tour Florida, Indian River Lagoon wildlife tour, Space Coast eco tour",
    },
    {
        "slug": "sunset-cruise",
        "name": "Sunset Cruise",
        "short_description": "Watch the Space Coast sunset over the Indian River Lagoon on a small-group Merritt Island evening cruise.",
        "long_description": (
            "End your day with a relaxing Merritt Island sunset cruise on the Indian River Lagoon near "
            "Cocoa Beach and Cape Canaveral. Bring your camera for golden-hour wildlife, calm water, "
            "and wide Space Coast sky views. Light snacks and drinks available on request."
        ),
        "duration_minutes": 90,
        "price_per_person": 60,
        "min_party": 3,
        "max_party": 6,
        "image_url": "/images/sunset.jpg",
        "sort_order": 2,
        "seo_title": "Sunset Cruise Merritt Island | Cocoa Beach Evening Boat Tour",
        "seo_description": "Book a small-group sunset cruise from Merritt Island near Cocoa Beach. Enjoy Indian River Lagoon views, wildlife, and Space Coast evening skies.",
        "seo_keywords": "Merritt Island sunset cruise, Cocoa Beach sunset boat tour, Space Coast evening cruise, Indian River Lagoon sunset, Cape Canaveral boat tour",
    },
    {
        "slug": "rocket-launch-viewing",
        "name": "Rocket Launch Viewing",
        "short_description": "Watch Space Coast rocket launches from the water near Cape Canaveral on a small-group boat tour.",
        "long_description": (
            "See launch-day views from the Indian River Lagoon with a local captain who knows the Space Coast. "
            "Rocket launch viewing trips are scheduled around official launch windows and combine open-water "
            "sightlines, wildlife, and Cape Canaveral stories for a memorable Florida experience."
        ),
        "duration_minutes": 120,
        "price_per_person": 60,
        "min_party": 3,
        "max_party": 6,
        "image_url": "/images/rocket.jpg",
        "sort_order": 3,
        "seo_title": "Rocket Launch Viewing Boat Tour | Cape Canaveral",
        "seo_description": "Book a Space Coast rocket launch viewing boat tour near Cape Canaveral and Cocoa Beach with Dolphin Island Tours.",
        "seo_keywords": "Cape Canaveral rocket launch boat tour, Space Coast rocket launch viewing, Cocoa Beach launch tour, Merritt Island rocket launch, Kennedy Space Center boat tour",
    },
]

DEFAULT_TIMES = [time(9, 0), time(12, 0), time(15, 0), time(18, 0)]

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
        "seo_title": "Merritt Island Dolphin Tours | Cocoa Beach Wildlife & Sunset Cruises",
        "seo_description": "Small-group Merritt Island boat tours near Cocoa Beach. See dolphins, manatees, birds, sunsets, and Space Coast rocket launches on the Indian River Lagoon.",
        "seo_keywords": "Merritt Island dolphin tours, Cocoa Beach wildlife tours, Indian River Lagoon boat tour, Space Coast sunset cruise, manatee sightseeing Florida, Cape Canaveral rocket launch boat tour",
        "hero_eyebrow": "Merritt Island · Cocoa Beach · Space Coast, FL",
        "hero_title": "Dolphin, wildlife, sunset, and rocket-launch boat tours.",
        "hero_subtitle": "Small-group tours from the Indian River Lagoon near Cocoa Beach and Cape Canaveral. See wild dolphins, manatees, birds, sunsets, and launch-day views with a local captain.",
        "primary_button_label": "Book a tour",
        "primary_button_url": "/tours",
        "secondary_button_label": "What you'll see",
        "secondary_button_url": "#highlights",
        "intro_eyebrow": "What you'll see",
        "intro_title": "A local Space Coast boat tour built around wildlife.",
        "section_one_title": "Book a Merritt Island boat tour.",
        "cta_title": "At the Harbortown marina.",
        "cta_body": "Tours leave on time - arrive 15 minutes early.",
    },
    "tours": {
        "hero": "tours_hero",
        "seo_title": "Merritt Island Boat Tours | Dolphin, Manatee & Sunset Cruises",
        "seo_description": "Compare Dolphin Island Tours wildlife excursions, dolphin and manatee tours, sunset cruises, and rocket launch viewing trips from Merritt Island, FL.",
        "seo_keywords": "Merritt Island boat tours, dolphin wildlife excursion, sunset cruise Merritt Island, Cocoa Beach boat tour, Space Coast boat tours, manatee tour Florida",
        "hero_eyebrow": "Pick your trip",
        "hero_title": "Merritt Island boat tours",
        "hero_subtitle": "Dolphin, manatee, wildlife, sunset, and rocket launch trips near Cocoa Beach. Small groups, $60 per person, 3 to 6 guests per boat.",
    },
    "book": {
        "seo_title": "Book a Tour | Dolphin Island Tours",
        "seo_description": "Book a Dolphin Island Tours boat tour.",
        "hero_title": "Book your Dolphin Island Tours trip.",
    },
    "reviews": {
        "seo_title": "Guest Reviews | Dolphin Island Tours",
        "seo_description": "Read verified guest reviews for Dolphin Island Tours across wildlife, sunset, dolphin, and Space Coast boat tours.",
        "hero_title": "Reviews from every tour.",
        "intro_title": "Guest reviews",
    },
    "about": {
        "hero": "about",
        "seo_title": "About Dolphin Island Tours | Local Space Coast Boat Captain",
        "seo_description": "Meet Dolphin Island Tours, a locally owned Merritt Island boat tour company sharing Indian River Lagoon dolphins, manatees, birds, sunsets, and Space Coast stories since 2010.",
        "seo_keywords": "local Merritt Island boat captain, Dolphin Island Tours about, Space Coast eco tour, Indian River Lagoon wildlife guide, Cocoa Beach dolphin tour company",
        "hero_eyebrow": "Our story",
        "hero_title": "A local Space Coast boat tour company.",
        "intro_body": "Dolphin Island Tours was founded in 2010 with a simple mission: share the wonder of the Space Coast with small groups of curious travelers. We run personal, affordable, eco-conscious boat tours from Merritt Island, Florida.",
        "section_one_title": "Our values",
    },
    "contact": {
        "hero": "contact_hero",
        "seo_title": "Contact Dolphin Island Tours | Merritt Island Boat Tour Questions",
        "seo_description": "Contact Dolphin Island Tours for Merritt Island dolphin tours, private charters, sunset cruises, rocket launch viewing trips, booking questions, and special requests.",
        "seo_keywords": "contact Merritt Island boat tour, Dolphin Island Tours phone, Cocoa Beach private boat charter, Space Coast tour questions, rocket launch boat tour booking",
        "hero_eyebrow": "Get in touch",
        "hero_title": "Questions about a tour or charter?",
        "section_one_title": "Reach us directly",
        "section_one_body": "We reply to every message within one business day.",
        "section_two_title": "Send a message",
        "cta_title": "Thanks - we got it.",
        "cta_body": "Check your inbox for a confirmation. We'll reply within one business day.",
    },
    "login": {
        "seo_title": "Login | Dolphin Island Tours",
        "seo_description": "Log in to your Dolphin Island Tours account.",
        "hero_title": "Log in to your account.",
    },
    "signup": {
        "seo_title": "Sign Up | Dolphin Island Tours",
        "seo_description": "Create a Dolphin Island Tours account.",
        "hero_title": "Create your Dolphin Island Tours account.",
    },
    "account": {
        "seo_title": "Account | Dolphin Island Tours",
        "seo_description": "Manage your Dolphin Island Tours account details and marketing email preferences.",
        "hero_title": "Account",
    },
    "bookings": {
        "seo_title": "My Bookings | Dolphin Island Tours",
        "seo_description": "Review your Dolphin Island Tours bookings and receipts.",
        "hero_title": "My bookings",
    },
    "forgot_password": {
        "seo_title": "Forgot Password | Dolphin Island Tours",
        "seo_description": "Request a Dolphin Island Tours password reset link.",
        "hero_title": "Reset your password.",
    },
    "reset_password": {
        "seo_title": "Reset Password | Dolphin Island Tours",
        "seo_description": "Set a new Dolphin Island Tours account password.",
        "hero_title": "Set a new password.",
    },
}


class Command(BaseCommand):
    help = "Seed Tours and the next 30 days of slots."

    def handle(self, *args, **opts):
        image_objects = {}
        for key, (path, alt) in SITE_IMAGES.items():
            obj, _ = SiteImage.objects.get_or_create(key=key, defaults={"default_path": path, "alt_text": alt})
            changed = []
            if not obj.default_path:
                obj.default_path = path
                changed.append("default_path")
            if not obj.alt_text:
                obj.alt_text = alt
                changed.append("alt_text")
            if changed:
                obj.save(update_fields=changed)
            image_objects[key] = obj
        self.stdout.write(f"Ensured {len(image_objects)} site image slots.")

        for page, defaults in PAGE_DEFAULTS.items():
            defaults = dict(defaults)
            hero = image_objects.get(defaults.pop("hero"))
            defaults["hero_image"] = hero
            _, created = PageContent.objects.get_or_create(page=page, defaults=defaults)
            self.stdout.write(f"{'created' if created else 'exists'} page content: {page}")

        for t in TOURS:
            obj, created = Tour.objects.update_or_create(slug=t["slug"], defaults=t)
            self.stdout.write(f"{'created' if created else 'updated'}: {obj.name}")

        today = timezone.now().date()
        created_n = 0
        for tour in Tour.objects.all():
            for d in range(1, 31):
                date = today + timedelta(days=d)
                for tm in DEFAULT_TIMES:
                    _, created = TourSlot.objects.get_or_create(
                        tour=tour, date=date, time=tm,
                        defaults={"capacity": 6, "is_active": True},
                    )
                    if created:
                        created_n += 1
        self.stdout.write(self.style.SUCCESS(f"Seeded {created_n} new slots."))
