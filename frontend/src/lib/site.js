import { useEffect, useMemo, useState } from "react";
import { api } from "./api.js";

const DEFAULT_SETTINGS = {
  site_name: "Dolphin Island Tours",
  tagline: "Small-group dolphin, wildlife, sunset, and rocket-launch boat tours on Florida's Space Coast.",
  seo_title: "Dolphin Island Tours | Merritt Island Dolphin & Sunset Boat Tours",
  seo_description: "Book small-group dolphin, manatee, wildlife, sunset, and rocket launch boat tours from Merritt Island near Cocoa Beach and Cape Canaveral.",
  seo_keywords: "Merritt Island dolphin tours, Cocoa Beach dolphin tour, Cape Canaveral boat tour, Space Coast wildlife tour, Indian River Lagoon tour, Florida sunset cruise, manatee tour Merritt Island, rocket launch boat tour",
  contact_email: "lewis@dolphinislandtours.com",
  contact_phone: "",
  address: "2700 Harbortown Drive, Merritt Island, FL",
  meeting_instructions: "Arrive 15 minutes before departure.",
  hours: "Open daily 9 AM - 5 PM",
  maps_url: "https://maps.google.com/?q=2700+Harbortown+Drive+Merritt+Island+FL",
  map_embed_url: "https://www.google.com/maps?q=2700+Harbortown+Drive+Merritt+Island+FL&output=embed",
  price_blurb: "$60 per person · 3-6 guests",
  tax_rate_percent: "0.00",
  review_count: 500,
  average_rating: "5.0",
  images: {},
  pages: {},
};

const DEFAULT_PAGES = {
  home: {
    seo_title: "Merritt Island Dolphin Tours | Cocoa Beach Wildlife & Sunset Cruises",
    seo_description: "Small-group Merritt Island boat tours near Cocoa Beach. See dolphins, manatees, birds, sunsets, and Space Coast rocket launches on the Indian River Lagoon.",
    seo_keywords: "Merritt Island dolphin tours, Cocoa Beach wildlife tours, Indian River Lagoon boat tour, Space Coast sunset cruise, manatee sightseeing Florida, Cape Canaveral rocket launch boat tour",
    hero_eyebrow: "Merritt Island · Cocoa Beach · Space Coast, FL",
    hero_title: "Dolphin, wildlife, sunset, and rocket-launch boat tours.",
    hero_subtitle: "Small-group tours from the Indian River Lagoon near Cocoa Beach and Cape Canaveral. See wild dolphins, manatees, birds, sunsets, and launch-day views with a local captain.",
    hero_image_url: "/images/hero-ocean.jpg",
    primary_button_label: "Book a tour",
    primary_button_url: "/tours",
    secondary_button_label: "What you'll see",
    secondary_button_url: "#highlights",
    intro_eyebrow: "What you'll see",
    intro_title: "A local Space Coast boat tour built around wildlife.",
    section_one_title: "Book a Merritt Island boat tour.",
    section_two_title: "500+ five-star trips.",
    cta_title: "At the Harbortown marina.",
    cta_body: "Tours leave on time - arrive 15 minutes early.",
  },
  tours: {
    seo_title: "Merritt Island Boat Tours | Dolphin, Manatee & Sunset Cruises",
    seo_description: "Compare Dolphin Island Tours wildlife excursions, dolphin and manatee tours, sunset cruises, and rocket launch viewing trips from Merritt Island, FL.",
    seo_keywords: "Merritt Island boat tours, dolphin wildlife excursion, sunset cruise Merritt Island, Cocoa Beach boat tour, Space Coast boat tours, manatee tour Florida",
    hero_eyebrow: "Pick your trip",
    hero_title: "Merritt Island boat tours",
    hero_subtitle: "Dolphin, manatee, wildlife, sunset, and rocket launch trips near Cocoa Beach. Small groups, $60 per person, 3 to 6 guests per boat.",
    hero_image_url: "/images/sunset-water.jpg",
  },
  about: {
    seo_title: "About Dolphin Island Tours | Local Space Coast Boat Captain",
    seo_description: "Meet Dolphin Island Tours, a locally owned Merritt Island boat tour company sharing Indian River Lagoon dolphins, manatees, birds, sunsets, and Space Coast stories since 2010.",
    seo_keywords: "local Merritt Island boat captain, Dolphin Island Tours about, Space Coast eco tour, Indian River Lagoon wildlife guide, Cocoa Beach dolphin tour company",
    hero_eyebrow: "Our story",
    hero_title: "A local Space Coast boat tour company.",
    hero_image_url: "/images/boat.jpg",
    intro_body: "Dolphin Island Tours was founded in 2010 with a simple mission: share the wonder of the Space Coast with small groups of curious travelers. We run personal, affordable, eco-conscious boat tours from Merritt Island, Florida.",
    section_one_title: "Our values",
  },
  contact: {
    seo_title: "Contact Dolphin Island Tours | Merritt Island Boat Tour Questions",
    seo_description: "Contact Dolphin Island Tours for Merritt Island dolphin tours, private charters, sunset cruises, rocket launch viewing trips, booking questions, and special requests.",
    seo_keywords: "contact Merritt Island boat tour, Dolphin Island Tours phone, Cocoa Beach private boat charter, Space Coast tour questions, rocket launch boat tour booking",
    hero_eyebrow: "Get in touch",
    hero_title: "Questions about a tour or charter?",
    hero_image_url: "/images/lagoon.jpg",
    section_one_title: "Reach us directly",
    section_one_body: "We reply to every message within one business day.",
    section_two_title: "Send a message",
    cta_title: "Thanks - we got it.",
    cta_body: "Check your inbox for a confirmation. We'll reply within one business day.",
  },
};

let siteCache = DEFAULT_SETTINGS;
let sitePromise = null;

function absolutize(src) {
  if (!src) return src;
  if (src.startsWith("http")) return src;
  return src;
}

export function imageFrom(settings, key, fallback) {
  return absolutize(settings?.images?.[key]?.image_url || fallback);
}

function loadSite() {
  if (!sitePromise) {
    sitePromise = api.site()
      .then((data) => {
        siteCache = { ...DEFAULT_SETTINGS, ...data };
        return siteCache;
      })
      .catch((error) => {
        sitePromise = null;
        throw error;
      });
  }
  return sitePromise;
}

export function preloadSite() {
  return loadSite().catch(() => DEFAULT_SETTINGS);
}

export function useSite(pageKey) {
  const [site, setSite] = useState(siteCache);

  useEffect(() => {
    let alive = true;
    loadSite().then((data) => {
      if (alive) setSite(data);
    }).catch(() => {});
    return () => { alive = false; };
  }, []);

  return useMemo(() => {
    const page = { ...(DEFAULT_PAGES[pageKey] || {}), ...(site.pages?.[pageKey] || {}) };
    return { site, page };
  }, [site, pageKey]);
}
