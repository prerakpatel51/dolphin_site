export const businessArea = [
  "Merritt Island",
  "Cocoa Beach",
  "Cape Canaveral",
  "Port Canaveral",
  "Brevard County",
  "Florida Space Coast",
  "Indian River Lagoon",
];

export const homeFaq = [
  ["What wildlife can we see on a Merritt Island boat tour?", "Guests often see bottlenose dolphins, manatees, pelicans, ospreys, shorebirds, and other Indian River Lagoon wildlife. Wildlife sightings vary by season and conditions."],
  ["Where do Dolphin Island Tours depart from?", "Tours depart from 2700 Harbortown Drive in Merritt Island, Florida, near Cocoa Beach, Cape Canaveral, and Port Canaveral."],
  ["Do you offer sunset cruises near Cocoa Beach?", "Yes. Dolphin Island Tours offers small-group sunset cruises on the Indian River Lagoon from Merritt Island."],
  ["Can we watch a rocket launch from the boat?", "Launch-day departures may be available when schedules and conditions line up. Contact Dolphin Island Tours before booking if rocket launch viewing is your main goal."],
  ["How many guests are on each tour?", "Tours are small-group experiences for 3 to 6 guests per boat."],
];

export function absoluteUrl(path) {
  if (!path) return undefined;
  if (path.startsWith("http")) return path;
  return window.location.origin + path;
}

export function localBusinessJsonLd(site, image) {
  const sameAs = [
    site.facebook_url,
    site.instagram_url,
    site.youtube_url,
    site.tiktok_url,
    site.tripadvisor_url,
    site.google_business_url,
  ].filter(Boolean);

  return {
    "@type": ["LocalBusiness", "TravelAgency", "TouristInformationCenter"],
    "@id": `${window.location.origin}/#business`,
    "name": site.site_name,
    "description": site.seo_description,
    "url": window.location.origin,
    "image": absoluteUrl(image || "/images/hero-ocean.jpg"),
    "logo": `${window.location.origin}/images/logo.png`,
    "telephone": site.contact_phone || undefined,
    "email": site.contact_email,
    "priceRange": site.price_blurb || "$60 per person",
    "address": {
      "@type": "PostalAddress",
      "streetAddress": "2700 Harbortown Drive",
      "addressLocality": "Merritt Island",
      "addressRegion": "FL",
      "addressCountry": "US",
    },
    "areaServed": businessArea.map(name => ({ "@type": "Place", "name": name })),
    "hasMap": site.maps_url,
    "sameAs": sameAs.length ? sameAs : undefined,
    "aggregateRating": {
      "@type": "AggregateRating",
      "ratingValue": String(site.average_rating),
      "reviewCount": String(site.review_count),
    },
  };
}

export function websiteJsonLd(site) {
  return {
    "@type": "WebSite",
    "@id": `${window.location.origin}/#website`,
    "url": window.location.origin,
    "name": site.site_name,
    "description": site.seo_description,
    "publisher": { "@id": `${window.location.origin}/#business` },
  };
}

export function breadcrumbJsonLd(items) {
  return {
    "@type": "BreadcrumbList",
    "itemListElement": items.map((item, index) => ({
      "@type": "ListItem",
      "position": index + 1,
      "name": item.name,
      "item": absoluteUrl(item.path),
    })),
  };
}

export function faqJsonLd(faqs) {
  return {
    "@type": "FAQPage",
    "mainEntity": faqs.map(([question, answer]) => ({
      "@type": "Question",
      "name": question,
      "acceptedAnswer": {
        "@type": "Answer",
        "text": answer,
      },
    })),
  };
}

export function graphJsonLd(nodes) {
  return {
    "@context": "https://schema.org",
    "@graph": nodes.filter(Boolean),
  };
}
