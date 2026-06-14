const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || "https://dolphinislandtours.com";

// Harbortown Marina, Merritt Island, FL.
const GEO = { latitude: 28.359, longitude: -80.7008 };

const AREA_SERVED = [
  "Merritt Island", "Cocoa Beach", "Cape Canaveral", "Port Canaveral", "Cocoa",
  "Rockledge", "Viera", "Suntree", "Melbourne", "West Melbourne", "Palm Bay",
  "Satellite Beach", "Indialantic", "Indian Harbour Beach", "Titusville", "Mims",
  "Brevard County", "Space Coast", "Kennedy Space Center",
].map((name) => ({ "@type": "City", name }));

function absolute(url) {
  if (!url) return undefined;
  return url.startsWith("http") ? url : `${SITE_URL}${url}`;
}

function sameAs(site) {
  return [site.facebook_url, site.instagram_url, site.youtube_url, site.tiktok_url,
    site.tripadvisor_url, site.google_business_url].filter(Boolean);
}

function ratingNode(site) {
  const count = Number(site.review_count || 0);
  const value = Number(site.average_rating || 0);
  if (!count || !value) return undefined;
  return {
    "@type": "AggregateRating",
    ratingValue: value.toFixed(1),
    reviewCount: count,
    bestRating: "5",
    worstRating: "1",
  };
}

export function localBusinessJsonLd(site, logoUrl) {
  return {
    "@context": "https://schema.org",
    "@type": ["TravelAgency", "TouristInformationCenter", "LocalBusiness"],
    "@id": `${SITE_URL}/#business`,
    name: site.site_name || "Dolphin Island Tours",
    description: site.seo_description,
    url: SITE_URL,
    telephone: site.contact_phone || undefined,
    email: site.contact_email || undefined,
    image: absolute(logoUrl) || `${SITE_URL}/images/hero-ocean.jpg`,
    logo: absolute(logoUrl) || `${SITE_URL}/images/logo.png`,
    priceRange: "$$",
    address: {
      "@type": "PostalAddress",
      streetAddress: "2700 Harbor Town Drive",
      addressLocality: "Merritt Island",
      addressRegion: "FL",
      postalCode: "32952",
      addressCountry: "US",
    },
    geo: { "@type": "GeoCoordinates", ...GEO },
    hasMap: site.maps_url || undefined,
    openingHours: "Mo-Su 09:00-17:00",
    areaServed: AREA_SERVED,
    sameAs: sameAs(site),
    aggregateRating: ratingNode(site),
    knowsAbout: [
      "dolphin watching tours", "manatee tours", "sunset cruises",
      "rocket launch viewing", "Indian River Lagoon wildlife tours",
      "private boat charters",
    ],
  };
}

export function websiteJsonLd(site) {
  return {
    "@context": "https://schema.org",
    "@type": "WebSite",
    "@id": `${SITE_URL}/#website`,
    url: SITE_URL,
    name: site.site_name || "Dolphin Island Tours",
    description: site.seo_description,
    publisher: { "@id": `${SITE_URL}/#business` },
    inLanguage: "en-US",
  };
}

export function tourJsonLd(tour, site) {
  if (!tour) return null;
  const url = `${SITE_URL}/tours/${tour.slug}`;
  const price = Number(tour.price_per_person || 0);
  return {
    "@context": "https://schema.org",
    "@type": ["TouristTrip", "Product"],
    name: tour.name,
    description: tour.seo_description || tour.short_description,
    image: absolute(tour.og_image_url || tour.image_url) || `${SITE_URL}/images/hero-ocean.jpg`,
    url,
    touristType: "Families, couples, and small private groups",
    provider: { "@id": `${SITE_URL}/#business` },
    offers: {
      "@type": "Offer",
      price: price.toFixed(2),
      priceCurrency: "USD",
      availability: "https://schema.org/InStock",
      url,
      category: "Boat tour",
    },
    aggregateRating: ratingNode(site),
  };
}

export function jsonLdScript(data) {
  // Strips undefined values so the emitted JSON-LD stays clean.
  return JSON.stringify(data, (_key, value) => (value === undefined ? undefined : value));
}
