from django.db import migrations


CORE_KEYWORDS = [
    "Dolphin Island Tours", "Dolphin Island Tours LLC", "Merritt Island dolphin tours", "Merritt Island boat tours",
    "Cocoa Beach dolphin tour", "Cocoa Beach boat tour", "Cape Canaveral boat tour", "Port Canaveral boat tour",
    "Kennedy Space Center boat tour", "Space Coast boat tours", "Florida Space Coast tours", "Indian River Lagoon tour",
    "Indian River Lagoon dolphin watching", "Indian River Lagoon wildlife tour", "Brevard County boat tour",
    "Harbortown Marina tour", "Harbor Town Drive Merritt Island", "private dolphin tour Merritt Island",
    "private boat tour Cocoa Beach", "small group dolphin tour Florida", "small group boat tour Merritt Island",
    "exclusive boat tour Space Coast", "family boat tour Merritt Island", "family dolphin watching Cocoa Beach",
    "couples boat tour Cocoa Beach", "romantic sunset cruise Merritt Island", "private sunset cruise Cocoa Beach",
    "Merritt Island sunset cruise", "Cocoa Beach sunset cruise", "Cape Canaveral sunset boat tour",
    "manatee tour Merritt Island", "Cocoa Beach manatee tour", "Florida manatee boat tour", "dolphin and manatee tour",
    "wildlife boat tour Cocoa Beach", "wildlife boat tour Merritt Island", "Florida dolphin watching",
    "dolphin watching near Orlando", "Orlando day trip dolphin tour", "Port Canaveral shore excursion",
    "cruise passenger boat tour", "Cape Canaveral cruise excursion", "Kennedy Space Center launch viewing",
    "rocket launch boat tour", "Cape Canaveral rocket launch boat", "Space Coast rocket launch viewing",
    "private rocket launch viewing", "eco tour Merritt Island", "Florida eco tour", "lagoon eco tour",
    "nature tour Cocoa Beach", "bird watching Indian River Lagoon", "pelican osprey wildlife tour",
    "boat charter Merritt Island", "private charter Merritt Island", "custom boat charter Cocoa Beach",
    "birthday boat tour Florida", "engagement boat tour Cocoa Beach", "special event boat tour",
    "BYOB private boat tour", "USCG captain boat tour", "licensed captain Merritt Island", "local boat tour guide",
    "safe family boat ride", "personal boat tour Florida", "uncrowded dolphin tour", "no crowded tour boat",
    "3 to 6 guest boat tour", "private small group tour", "Merritt Island things to do", "Cocoa Beach things to do",
    "Cape Canaveral things to do", "Port Canaveral activities", "Brevard County family activities",
    "Space Coast vacation activities", "beach vacation boat tour", "Florida wildlife sightseeing",
    "lagoon sightseeing cruise", "dolphin photo tour", "sunset photo cruise", "waterfront experience Merritt Island",
    "tourist attraction Merritt Island", "best dolphin tour Cocoa Beach", "best boat tour Merritt Island",
    "book dolphin tour online", "online boat tour booking", "email confirmation boat tour", "download tour receipt",
    "Google reviews Dolphin Island Tours", "Dolphin Island Tours Google review", "Dolphin Island Tours reviews",
    "Merritt Island tour reviews", "Cocoa Beach boat tour reviews", "private tour reviews Space Coast",
]


def keyword_set(*groups):
    values = []
    for group in groups:
        values.extend(group)
    values.extend(CORE_KEYWORDS)
    return ", ".join(values)


PAGE_KEYWORDS = {
    "home": keyword_set([
        "private Merritt Island dolphin tours home page", "book Cocoa Beach dolphin tour online",
        "Dolphin Island Tours official website", "Merritt Island wildlife cruise",
        "small group Space Coast sightseeing", "private Indian River Lagoon experience",
        "dolphin tour near Cocoa Beach Pier", "boat tours near Cape Canaveral hotels",
        "family friendly dolphin watching", "Space Coast vacation boat ride",
        "custom Merritt Island water tour", "relaxed Florida lagoon cruise",
    ]),
    "tours": keyword_set([
        "compare Merritt Island boat tours", "dolphin wildlife excursion booking", "sunset cruise availability",
        "rocket launch tour availability", "tour dates and times Merritt Island", "boat tour prices Cocoa Beach",
        "private tour departure times", "small group tour capacity", "Merritt Island tour schedule",
        "book wildlife tour Space Coast", "book sunset cruise Cocoa Beach", "book rocket launch boat tour",
    ]),
    "reviews": keyword_set([
        "Dolphin Island Tours Google reviews", "write Google review Dolphin Island Tours", "view Google reviews",
        "Merritt Island dolphin tour reviews", "Cocoa Beach boat tour reviews", "Space Coast private tour reviews",
        "customer reviews dolphin tour", "guest reviews sunset cruise", "private boat tour ratings",
        "Dolphin Island Tours review link", "Dolphin Island Tours business profile", "Google Business Profile reviews",
    ]),
    "about": keyword_set([
        "about Dolphin Island Tours", "local Merritt Island tour company", "locally owned boat tour business",
        "Space Coast captain", "private tour captain Merritt Island", "Cocoa Beach boat tour company",
        "Indian River Lagoon local guide", "family owned Florida tour business", "USCG certified captain tour",
        "personal Florida wildlife guide", "safe private boat experience", "authentic Space Coast boat tour",
    ]),
    "contact": keyword_set([
        "contact Dolphin Island Tours", "Dolphin Island Tours phone number", "Dolphin Island Tours email",
        "Merritt Island boat tour questions", "private charter questions Cocoa Beach", "custom tour request",
        "rocket launch viewing request", "sunset cruise questions", "group booking questions",
        "Harbortown Marina directions", "boat tour meeting point", "Dolphin Island Tours address",
    ]),
    "book": keyword_set([
        "book Dolphin Island Tours", "secure boat tour checkout", "Merritt Island tour booking",
        "Cocoa Beach dolphin tour reservation", "private boat tour payment", "Square checkout boat tour",
        "tour confirmation email", "download booking receipt", "guest checkout boat tour",
        "no login booking", "promo code dolphin tour", "online tour reservation Florida",
    ]),
    "find_booking": keyword_set([
        "find Dolphin Island Tours booking", "download Dolphin Island Tours receipt", "lookup boat tour confirmation",
        "find booking by email", "tour receipt download", "guest booking lookup", "booking confirmation lookup",
        "Merritt Island tour receipt", "Cocoa Beach tour confirmation", "boat tour booking status",
        "retrieve tour confirmation", "download boat tour receipt",
    ]),
    "bookings": keyword_set([
        "Dolphin Island Tours booking history", "logged in tour receipts", "customer booking account",
        "private tour receipt history", "Merritt Island booking record", "Cocoa Beach tour receipt",
    ]),
    "account": keyword_set([
        "Dolphin Island Tours account", "manage tour account", "marketing email preferences",
        "saved customer profile", "logged in booking history", "customer account boat tour",
    ]),
    "login": keyword_set(["Dolphin Island Tours login", "customer login boat tour", "manage booking login"]),
    "signup": keyword_set(["Dolphin Island Tours signup", "create tour account", "customer account registration"]),
    "forgot_password": keyword_set(["Dolphin Island Tours password reset", "forgot account password", "secure reset link"]),
    "reset_password": keyword_set(["set new Dolphin Island Tours password", "secure account password", "reset account access"]),
}


PAGE_DESCRIPTIONS = {
    "find_booking": "Find your Dolphin Island Tours booking with your email and last name, then download your confirmation receipt without creating an account.",
    "book": "Book a Dolphin Island Tours boat tour through guest checkout with contact details, traveler information, promo code support, secure Square payment, email confirmation, and receipt download.",
}


def apply_keywords(apps, schema_editor):
    SiteSettings = apps.get_model("api", "SiteSettings")
    PageContent = apps.get_model("api", "PageContent")
    Tour = apps.get_model("api", "Tour")

    settings, _ = SiteSettings.objects.get_or_create(pk=1)
    settings.seo_keywords = keyword_set([
        "Dolphin Island Tours official site", "private Merritt Island boat tour company",
        "Cocoa Beach dolphin watching reservations",
    ])
    settings.save(update_fields=["seo_keywords"])

    for page, keywords in PAGE_KEYWORDS.items():
        defaults = {"seo_keywords": keywords}
        if page in PAGE_DESCRIPTIONS:
            defaults["seo_description"] = PAGE_DESCRIPTIONS[page]
        if page == "find_booking":
            defaults.update({
                "seo_title": "Find My Booking | Dolphin Island Tours",
                "hero_eyebrow": "Booking lookup",
                "hero_title": "Find your booking",
            })
        PageContent.objects.update_or_create(page=page, defaults=defaults)

    for tour in Tour.objects.all():
        tour.seo_keywords = keyword_set([
            tour.name,
            f"{tour.name} Merritt Island",
            f"{tour.name} Cocoa Beach",
            f"book {tour.name}",
            f"private {tour.name}",
            f"{tour.name} Space Coast",
        ])
        tour.save(update_fields=["seo_keywords"])


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0032_allow_guest_bookings"),
    ]

    operations = [
        migrations.RunPython(apply_keywords, migrations.RunPython.noop),
    ]
