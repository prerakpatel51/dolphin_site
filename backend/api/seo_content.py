"""Canonical SEO copy for Dolphin Island Tours.

Single source of truth for meta titles, descriptions, and keywords used by the
``optimize_seo`` management command. Descriptions are kept near ~155 characters
so Google does not truncate them, and keywords blanket the full Space Coast /
Brevard County service area (Merritt Island, Cocoa Beach, Cape Canaveral, Port
Canaveral, Cocoa, Rockledge, Viera, Suntree, Melbourne, West Melbourne, Palm
Bay, Satellite Beach, Indialantic, Indian Harbour Beach, Titusville, Mims,
Kennedy Space Center, Indian River Lagoon, and the Banana River).
"""

# Shared geographic + service keywords reused across pages.
GEO = (
    "Merritt Island, Cocoa Beach, Cape Canaveral, Port Canaveral, Cocoa, Rockledge, "
    "Viera, Suntree, Melbourne FL, West Melbourne, Palm Bay, Satellite Beach, Indialantic, "
    "Indian Harbour Beach, Titusville, Mims, Brevard County, Space Coast, Kennedy Space Center, "
    "Indian River Lagoon, Banana River"
)

SITE = {
    "site_name": "Dolphin Island Tours",
    "tagline": "Private Space Coast boat tours, dolphin watching, sunset cruises, and rocket launch viewing.",
    "seo_title": "Dolphin Island Tours | Space Coast Boat Tours & Dolphin Watching FL",
    "seo_description": (
        "Private Space Coast boat tours from Merritt Island, FL — dolphin watching, sunset "
        "cruises & rocket launch viewing. Small groups of 3–6. Book online."
    ),
    "seo_keywords": (
        "boat tours Space Coast, dolphin tours Florida, dolphin watching Merritt Island, Cocoa Beach boat tour, "
        "Melbourne FL boat tour, Brevard County boat tours, manatee tour, sunset cruise, rocket launch boat tour, "
        "Indian River Lagoon tour, private boat charter Florida, Dolphin Island Tours, things to do Cocoa Beach, "
        f"things to do Space Coast, boat tours near me, {GEO}"
    ),
}

PAGES = {
    "home": {
        "seo_title": "Space Coast Dolphin & Boat Tours | Merritt Island, Cocoa Beach FL",
        "seo_description": (
            "Private dolphin, sunset, wildlife & rocket-launch boat tours on Florida's Space "
            "Coast. Small groups of 3–6 from Merritt Island near Cocoa Beach. Book online."
        ),
        "seo_keywords": (
            "Space Coast boat tours, dolphin tours Merritt Island, Cocoa Beach dolphin watching, "
            "Melbourne FL boat tour, Viera boat tour, Rockledge boat tour, Titusville dolphin tour, "
            "manatee tour Brevard County, sunset cruise Cocoa Beach, rocket launch viewing boat, "
            f"private boat charter Space Coast, Indian River Lagoon wildlife tour, {GEO}"
        ),
    },
    "tours": {
        "seo_title": "Boat Tours on the Space Coast | Dolphin, Sunset & Launch Cruises",
        "seo_description": (
            "Private Space Coast boat tours from Merritt Island, FL — dolphin & manatee trips, "
            "sunset cruises & rocket launch viewing. Small groups of 3–6. Book online."
        ),
        "seo_keywords": (
            "Space Coast boat tours, dolphin wildlife excursion, sunset cruise Merritt Island, "
            "rocket launch boat tour Cape Canaveral, manatee tour Cocoa Beach, private boat tour Melbourne FL, "
            f"eco tour Indian River Lagoon, small group boat tour Brevard County, {GEO}"
        ),
    },
    "about": {
        "seo_title": "About Dolphin Island Tours | Local Space Coast Boat Tour Company",
        "seo_description": (
            "Locally owned Merritt Island boat tours — private dolphin, sunset, wildlife & rocket "
            "launch cruises on Florida's Space Coast. Meet the captain & book online."
        ),
        "seo_keywords": (
            "about Dolphin Island Tours, local boat tour company Space Coast, Merritt Island captain, "
            "family owned boat tour Cocoa Beach, private charter Brevard County, "
            f"Indian River Lagoon eco tour, {GEO}"
        ),
    },
    "contact": {
        "seo_title": "Contact Dolphin Island Tours | Book a Space Coast Boat Tour",
        "seo_description": (
            "Contact Dolphin Island Tours in Merritt Island, FL for private dolphin tours, sunset "
            "cruises & rocket launch trips across the Space Coast. Call or message us today."
        ),
        "seo_keywords": (
            "contact Dolphin Island Tours, book boat tour Merritt Island, private charter inquiry, "
            f"Cocoa Beach boat tour phone, Space Coast tour booking, {GEO}"
        ),
    },
    "reviews": {
        "seo_title": "Reviews | Dolphin Island Tours — Space Coast Boat Tours FL",
        "seo_description": (
            "Read 5-star reviews for Dolphin Island Tours — see why guests love our private "
            "Merritt Island & Cocoa Beach dolphin, sunset & wildlife boat tours."
        ),
        "seo_keywords": (
            "Dolphin Island Tours reviews, best boat tour Cocoa Beach, top dolphin tour Merritt Island, "
            f"5 star Space Coast boat tour, Melbourne FL boat tour reviews, {GEO}"
        ),
    },
    "book": {
        "seo_title": "Book a Space Coast Boat Tour | Dolphin Island Tours, FL",
        "seo_description": (
            "Book your private Merritt Island boat tour online — dolphin watching, sunset cruise, "
            "wildlife or rocket launch viewing on Florida's Space Coast."
        ),
        "seo_keywords": (
            "book boat tour Merritt Island, reserve dolphin tour Cocoa Beach, online boat tour booking, "
            f"private sunset cruise booking, Space Coast tour reservation, {GEO}"
        ),
    },
    "find_booking": {
        "seo_title": "Find Your Booking | Dolphin Island Tours",
        "seo_description": (
            "Look up your Dolphin Island Tours reservation with your email and last name to view your "
            "confirmation and download your receipt."
        ),
        "seo_keywords": (
            "Dolphin Island Tours booking lookup, find my boat tour reservation, "
            "download tour receipt, Space Coast boat tour confirmation"
        ),
    },
}

TOURS = {
    "dolphin-wildlife-excursion": {
        "seo_title": "Private Dolphin & Wildlife Tour | Merritt Island, Cocoa Beach FL",
        "seo_description": (
            "See wild dolphins, manatees & lagoon wildlife on a private Merritt Island boat tour "
            "near Cocoa Beach. Small groups of 3–6. Book online."
        ),
        "seo_keywords": (
            "dolphin tour Merritt Island, dolphin watching Cocoa Beach, manatee tour Florida, "
            "private wildlife boat tour, Indian River Lagoon eco tour, Melbourne FL dolphin tour, "
            f"Viera Rockledge boat tour, small group dolphin cruise, {GEO}"
        ),
    },
    "sunset-cruise": {
        "seo_title": "Private Sunset Cruise | Merritt Island & Cocoa Beach, FL",
        "seo_description": (
            "Relax on a private Indian River Lagoon sunset cruise near Cocoa Beach & Merritt Island. "
            "Golden-hour wildlife, just 3–6 guests. Book online."
        ),
        "seo_keywords": (
            "sunset cruise Merritt Island, Cocoa Beach sunset boat tour, private evening cruise Florida, "
            "Indian River Lagoon sunset, romantic boat tour Melbourne FL, Space Coast sunset cruise, "
            f"proposal boat tour, {GEO}"
        ),
    },
    "rocket-launch-viewing": {
        "seo_title": "Rocket Launch Boat Tour | Cape Canaveral & Kennedy Space Center",
        "seo_description": (
            "Watch a rocket launch from the water on a private boat tour near Cape Canaveral & "
            "Kennedy Space Center. Small Space Coast groups of 3–6. Book online."
        ),
        "seo_keywords": (
            "rocket launch boat tour, Cape Canaveral launch viewing, Kennedy Space Center boat tour, "
            "SpaceX launch viewing boat, Merritt Island rocket launch, Cocoa Beach launch tour, "
            f"Space Coast rocket launch, {GEO}"
        ),
    },
}


def tour_seo(tour):
    """SEO for a tour: use the curated map, else generate strong defaults.

    Ensures any tour added later automatically gets ranking-ready metadata.
    """
    curated = TOURS.get(tour.slug)
    if curated:
        return curated
    name = tour.name
    return {
        "seo_title": f"{name} | Space Coast Boat Tour, Merritt Island FL"[:70],
        "seo_description": (
            f"Book the {name} with Dolphin Island Tours — a private Space Coast boat tour from "
            f"Merritt Island near Cocoa Beach. Small groups of 3–6. Book online."
        )[:300],
        "seo_keywords": (
            f"{name}, {name} Merritt Island, {name} Cocoa Beach, private boat tour Space Coast, "
            f"Brevard County boat tour, {GEO}"
        ),
    }
