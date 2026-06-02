from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, time
from api.models import FAQItem, Tour, TourSlot, SiteImage, PageContent


TOURS = [
    {
        "slug": "dolphin-wildlife-excursion",
        "name": "Dolphin Wildlife Excursion",
        "short_description": "Private-style Merritt Island dolphin and wildlife tour near Cocoa Beach for families, couples, and small groups.",
        "long_description": (
            "Cruise the protected Indian River Lagoon around Merritt Island looking for wild bottlenose "
            "dolphins, manatees, ospreys, pelicans, shorebirds, and Space Coast scenery. This personal "
            "small-group wildlife tour is close to Cocoa Beach, Cape Canaveral, Port Canaveral, and "
            "Kennedy Space Center. With only 3 to 6 guests, the trip feels private, relaxed, and easy to "
            "shape around your group, from family sightseeing to exclusive wildlife time on the water."
        ),
        "duration_minutes": 120,
        "price_per_person": 60,
        "min_party": 3,
        "max_party": 6,
        "image_url": "/images/dolphin.jpg",
        "sort_order": 1,
        "seo_title": "Private Dolphin Wildlife Tour | Merritt Island & Cocoa Beach",
        "seo_description": "Book a private-style Merritt Island dolphin and manatee wildlife tour near Cocoa Beach, Cape Canaveral, and the Indian River Lagoon.",
        "seo_keywords": "private dolphin tour Merritt Island, Cocoa Beach dolphin tour, manatee tour, Indian River Lagoon wildlife tour, Space Coast eco tour, exclusive boat tour",
    },
    {
        "slug": "sunset-cruise",
        "name": "Sunset Cruise",
        "short_description": "Private-style Merritt Island sunset cruise near Cocoa Beach with calm water, wildlife, and Space Coast views.",
        "long_description": (
            "End your day with a relaxing Merritt Island sunset cruise on the Indian River Lagoon near "
            "Cocoa Beach, Cape Canaveral, and Port Canaveral. Bring your camera for golden-hour wildlife, "
            "calm water, and wide Space Coast sky views. The boat is limited to 3 to 6 guests, making it "
            "a personal evening cruise for couples, families, proposals, birthdays, and exclusive groups. "
            "Ask before booking about private-trip preferences and what can be safely accommodated."
        ),
        "duration_minutes": 90,
        "price_per_person": 60,
        "min_party": 3,
        "max_party": 6,
        "image_url": "/images/sunset.jpg",
        "sort_order": 2,
        "seo_title": "Private Sunset Cruise Merritt Island | Cocoa Beach Boat Tour",
        "seo_description": "Book a private-style Merritt Island sunset cruise near Cocoa Beach and Cape Canaveral with Indian River Lagoon views and wildlife.",
        "seo_keywords": "private sunset cruise Merritt Island, Cocoa Beach sunset boat tour, exclusive evening cruise, Indian River Lagoon sunset, Cape Canaveral boat tour",
    },
    {
        "slug": "rocket-launch-viewing",
        "name": "Rocket Launch Viewing",
        "short_description": "Watch Space Coast rocket launches from the water on a personal boat tour near Cape Canaveral.",
        "long_description": (
            "See launch-day views from the Indian River Lagoon with a local captain who knows the Space Coast. "
            "Rocket launch viewing trips are scheduled around official launch windows and combine open-water "
            "sightlines, wildlife, and Cape Canaveral stories for a memorable Florida experience. With only "
            "3 to 6 guests, your group gets a more private, flexible, and exclusive way to watch launches "
            "near Cape Canaveral, Cocoa Beach, Port Canaveral, and Kennedy Space Center."
        ),
        "duration_minutes": 120,
        "price_per_person": 60,
        "min_party": 3,
        "max_party": 6,
        "image_url": "/images/rocket.jpg",
        "sort_order": 3,
        "seo_title": "Private Rocket Launch Boat Tour | Cape Canaveral",
        "seo_description": "Book a private-style rocket launch viewing boat tour near Cape Canaveral, Cocoa Beach, Kennedy Space Center, and Merritt Island.",
        "seo_keywords": "Cape Canaveral rocket launch boat tour, private launch viewing, Space Coast rocket launch, Cocoa Beach launch tour, Kennedy Space Center boat tour",
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
        "seo_title": "Private Merritt Island Dolphin Tours | Cocoa Beach Boat Tours",
        "seo_description": "Book private and small-group Merritt Island dolphin tours, sunset cruises, wildlife trips, and rocket launch boat tours near Cocoa Beach.",
        "seo_keywords": "Merritt Island dolphin tours, private boat tour Cocoa Beach, exclusive boat tours, Cape Canaveral rocket launch boat tour, Indian River Lagoon, sunset cruise, manatee tour",
        "hero_eyebrow": "Merritt Island · Cocoa Beach · Space Coast, FL",
        "hero_title": "Private-Style Dolphin, Sunset, and Rocket Launch Boat Tours",
        "hero_subtitle": "Personal Merritt Island boat tours for dolphin watching, manatees, sunsets, rocket launch viewing, and exclusive days on the water near Cocoa Beach.",
        "primary_button_label": "Book a tour",
        "primary_button_url": "/tours",
        "secondary_button_label": "What you'll see",
        "secondary_button_url": "#highlights",
        "intro_eyebrow": "What you'll see",
        "intro_title": "A personal Space Coast boat tour built around your group.",
        "section_one_title": "Book a private-style Merritt Island boat tour.",
        "cta_title": "At the Harbortown marina.",
        "cta_body": "Tours leave on time - arrive 15 minutes early.",
    },
    "tours": {
        "hero": "tours_hero",
        "seo_title": "Private Merritt Island Boat Tours | Dolphin, Sunset & Launch",
        "seo_description": "Compare private-style Merritt Island boat tours for dolphins, manatees, sunset cruises, exclusive trips, and rocket launch viewing.",
        "seo_keywords": "private Merritt Island boat tours, exclusive boat tours, Cocoa Beach boat tour, dolphin wildlife excursion, sunset cruise, manatee tour, rocket launch boat",
        "hero_eyebrow": "Pick your trip",
        "hero_title": "Private-style Merritt Island boat tours",
        "hero_subtitle": "Dolphin, manatee, wildlife, sunset, and rocket launch trips near Cocoa Beach. Personal tours, $60 per person, 3 to 6 guests per boat.",
    },
    "book": {
        "seo_title": "Book a Tour | Dolphin Island Tours",
        "seo_description": "Book a Dolphin Island Tours boat tour.",
        "hero_title": "Book your Dolphin Island Tours trip.",
    },
    "reviews": {
        "seo_title": "Dolphin Island Tours Reviews | Merritt Island Boat Tours",
        "seo_description": "Read verified guest reviews for private-style Merritt Island dolphin tours, sunset cruises, wildlife trips, and Space Coast boat tours.",
        "hero_title": "Reviews from every tour.",
        "intro_title": "Guest reviews",
    },
    "about": {
        "hero": "about",
        "seo_title": "About Dolphin Island Tours | Private Space Coast Boat Tours",
        "seo_description": "Meet Dolphin Island Tours, a locally owned Merritt Island boat tour company offering personal dolphin, sunset, wildlife, and launch trips.",
        "seo_keywords": "private Space Coast boat tours, local Merritt Island captain, Cocoa Beach dolphin tour company, Indian River Lagoon guide, exclusive boat tour",
        "hero_eyebrow": "About us",
        "hero_title": "About Dolphin Island Tours",
        "intro_title": "Welcome aboard.",
        "intro_body": (
            "Welcome to Dolphin Island Tours, where unforgettable memories meet the beauty of Florida's coastline. "
            "Based in Merritt Island, we created our dolphin tour company from a love of the water, wildlife, and "
            "sharing the natural beauty of the Space Coast with others.\n\n"
            "What started as a dream quickly became a mission to give families, couples, and visitors a relaxing "
            "and exciting way to experience dolphins in their natural habitat.\n\n"
            "Our tours are designed to feel personal, private, welcoming, and authentic. Whether you're spotting "
            "playful dolphins, enjoying a breathtaking sunset, planning an exclusive family trip, or simply "
            "relaxing on the water, we want every guest to leave with memories they'll never forget.\n\n"
            "We are proud to be locally owned and operated, and we can't wait to welcome you aboard."
        ),
        "section_one_title": "Personal, private-style, and authentic.",
        "section_one_body": "Every trip is built around small groups, local knowledge, and a relaxed Space Coast experience with no crowded tour boat feel.",
    },
    "contact": {
        "hero": "contact_hero",
        "seo_title": "Contact Dolphin Island Tours | Private Boat Tour Questions",
        "seo_description": "Contact Dolphin Island Tours for private Merritt Island boat tours, dolphin trips, sunset cruises, launch viewing, and custom requests.",
        "seo_keywords": "contact private boat tour, Merritt Island dolphin tour phone, Cocoa Beach private charter, exclusive boat tour questions, rocket launch boat booking",
        "hero_eyebrow": "Get in touch",
        "hero_title": "Questions about a private or custom boat tour?",
        "section_one_title": "Reach us directly",
        "section_one_body": "Ask about private tours, exclusive trips, custom timing, onboard preferences, celebrations, wildlife tours, sunset cruises, and rocket launch viewing.",
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

FAQ_DEFAULTS = [
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
            hero_key = defaults.pop("hero", None)
            if hero_key:
                defaults["hero_image"] = image_objects.get(hero_key)
            _, created = PageContent.objects.get_or_create(page=page, defaults=defaults)
            self.stdout.write(f"{'created' if created else 'exists'} page content: {page}")

        for t in TOURS:
            obj, created = Tour.objects.get_or_create(slug=t["slug"], defaults=t)
            self.stdout.write(f"{'created' if created else 'exists'}: {obj.name}")

        for index, (question, answer) in enumerate(FAQ_DEFAULTS, start=1):
            FAQItem.objects.get_or_create(
                question=question,
                defaults={"answer": answer, "sort_order": index, "is_active": True},
            )
        self.stdout.write(f"Ensured {len(FAQ_DEFAULTS)} FAQ items.")

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
