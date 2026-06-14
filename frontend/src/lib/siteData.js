const GOOGLE_BUSINESS_QUERY = "Dolphin Island Tours LLC 2700 Harbortown Dr Merritt Island FL 32952";
const GOOGLE_BUSINESS_QUERY_ENCODED = encodeURIComponent(GOOGLE_BUSINESS_QUERY);

export const DEFAULT_GOOGLE_BUSINESS_URL = "https://share.google/Ig5FtVIQGXBWMUIGC";
export const DEFAULT_GOOGLE_REVIEWS_URL = "https://share.google/Ig5FtVIQGXBWMUIGC";
export const DEFAULT_GOOGLE_REVIEW_URL = "https://g.page/r/CehBxKNRm1TfEBM/review";
export const DEFAULT_GOOGLE_REVIEWS_EMBED_URL = `https://www.google.com/maps?q=${GOOGLE_BUSINESS_QUERY_ENCODED}&output=embed`;

const CORE_SEO_KEYWORDS = [
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
  "Merritt Island tour reviews", "Cocoa Beach boat tour reviews", "private tour reviews Space Coast"
];

const keywordSet = (...groups) => groups.flat().concat(CORE_SEO_KEYWORDS).join(", ");

const HOME_SEO_KEYWORDS = keywordSet([
  "private Merritt Island dolphin tours home page", "book Cocoa Beach dolphin tour online", "Dolphin Island Tours official website",
  "Merritt Island wildlife cruise", "small group Space Coast sightseeing", "private Indian River Lagoon experience",
  "dolphin tour near Cocoa Beach Pier", "boat tours near Cape Canaveral hotels", "family friendly dolphin watching",
  "Space Coast vacation boat ride", "custom Merritt Island water tour", "relaxed Florida lagoon cruise"
]);

const TOURS_SEO_KEYWORDS = keywordSet([
  "compare Merritt Island boat tours", "dolphin wildlife excursion booking", "sunset cruise availability",
  "rocket launch tour availability", "tour dates and times Merritt Island", "boat tour prices Cocoa Beach",
  "private tour departure times", "small group tour capacity", "Merritt Island tour schedule",
  "book wildlife tour Space Coast", "book sunset cruise Cocoa Beach", "book rocket launch boat tour"
]);

const ABOUT_SEO_KEYWORDS = keywordSet([
  "about Dolphin Island Tours", "local Merritt Island tour company", "locally owned boat tour business",
  "Space Coast captain", "private tour captain Merritt Island", "Cocoa Beach boat tour company",
  "Indian River Lagoon local guide", "family owned Florida tour business", "USCG certified captain tour",
  "personal Florida wildlife guide", "safe private boat experience", "authentic Space Coast boat tour"
]);

const CONTACT_SEO_KEYWORDS = keywordSet([
  "contact Dolphin Island Tours", "Dolphin Island Tours phone number", "Dolphin Island Tours email",
  "Merritt Island boat tour questions", "private charter questions Cocoa Beach", "custom tour request",
  "rocket launch viewing request", "sunset cruise questions", "group booking questions",
  "Harbortown Marina directions", "boat tour meeting point", "Dolphin Island Tours address"
]);

const REVIEWS_SEO_KEYWORDS = keywordSet([
  "Dolphin Island Tours Google reviews", "write Google review Dolphin Island Tours", "view Google reviews",
  "Merritt Island dolphin tour reviews", "Cocoa Beach boat tour reviews", "Space Coast private tour reviews",
  "customer reviews dolphin tour", "guest reviews sunset cruise", "private boat tour ratings",
  "Dolphin Island Tours review link", "Dolphin Island Tours business profile", "Google Business Profile reviews"
]);

const BOOK_SEO_KEYWORDS = keywordSet([
  "book Dolphin Island Tours", "secure boat tour checkout", "Merritt Island tour booking",
  "Cocoa Beach dolphin tour reservation", "private boat tour payment", "Square checkout boat tour",
  "tour confirmation email", "download booking receipt", "guest checkout boat tour",
  "no login booking", "promo code dolphin tour", "online tour reservation Florida"
]);

const FIND_BOOKING_SEO_KEYWORDS = keywordSet([
  "find Dolphin Island Tours booking", "download Dolphin Island Tours receipt", "lookup boat tour confirmation",
  "find booking by email", "tour receipt download", "guest booking lookup", "booking confirmation lookup",
  "Merritt Island tour receipt", "Cocoa Beach tour confirmation", "boat tour booking status",
  "retrieve tour confirmation", "download boat tour receipt"
]);

const ACCOUNT_SEO_KEYWORDS = keywordSet([
  "Dolphin Island Tours account", "manage tour account", "marketing email preferences",
  "saved customer profile", "logged in booking history", "customer account boat tour",
  "account settings Dolphin Island Tours", "tour customer profile"
]);

export const DEFAULT_SETTINGS = {
  site_name: "Dolphin Island Tours",
  tagline: "Creating unforgettable dolphin encounters on Florida's Space Coast.",
  seo_title: "Dolphin Island Tours | Private Merritt Island Boat Tours",
  seo_description: "Dolphin Island Tours LLC offers private and small-group boat tours from Merritt Island, Florida, near Cocoa Beach, Cape Canaveral, Port Canaveral, Kennedy Space Center, and the Indian River Lagoon. Guests can book dolphin watching trips, manatee and wildlife tours, sunset cruises, rocket launch viewing trips, family boat tours, couples cruises, custom private charters, and relaxed Space Coast sightseeing on the water. Tours are designed for personal service, local wildlife viewing, calm lagoon scenery, memorable photos, and easy access from Cocoa Beach, Orlando day trips, cruise port visits, beach vacations, and Brevard County stays.",
  seo_keywords: keywordSet(["Dolphin Island Tours official site", "private Merritt Island boat tour company", "Cocoa Beach dolphin watching reservations"]),
  contact_email: "lauren@dolphinislandtours.com",
  contact_phone: "321-390-0176",
  address: "2700 Harbor Town Drive, Merritt Island, FL 32952",
  meeting_instructions: "Arrive 15 minutes before departure.",
  hours: "Open daily 9 AM - 5 PM",
  maps_url: "https://maps.google.com/?q=2700+Harbor+Town+Drive+Merritt+Island+FL+32952",
  map_embed_url: "https://www.google.com/maps?q=2700+Harbor+Town+Drive+Merritt+Island+FL+32952&output=embed",
  price_blurb: "$60 per person · 3-6 guests",
  review_count: 1,
  average_rating: "5.0",
  google_business_url: DEFAULT_GOOGLE_BUSINESS_URL,
  google_review_url: DEFAULT_GOOGLE_REVIEW_URL,
  google_reviews_url: DEFAULT_GOOGLE_REVIEWS_URL,
  google_reviews_embed_url: DEFAULT_GOOGLE_REVIEWS_EMBED_URL,
  footer_legal_text: "Copyright © 2026 Dolphin Island Tours LLC | Licensed & Insured | USCG Certified Captain",
  images: {},
  pages: {},
  faqs: [
    {
      question: "Can we book a private or exclusive boat tour?",
      answer: "Yes. Dolphin Island Tours specializes in private and small-group trips for 3 to 6 guests, so your group can enjoy the boat without joining a crowd. Contact us for private tour requests, celebrations, and custom timing.",
    },
    {
      question: "Are alcohol, smoking, or special onboard preferences allowed?",
      answer: "Private trips may be able to accommodate personal preferences when the captain, guests, safety rules, and marina policies allow it. Tell us what you have in mind before booking so we can confirm what is possible for your group.",
    },
    {
      question: "What wildlife can we see on a Merritt Island boat tour?",
      answer: "Guests often see bottlenose dolphins, manatees, pelicans, ospreys, shorebirds, and other Indian River Lagoon wildlife. Sightings vary by season, weather, tide, and conditions.",
    },
    {
      question: "Where do Dolphin Island Tours depart from?",
      answer: "Tours depart from 2700 Harbor Town Drive in Merritt Island, Florida, near Cocoa Beach, Cape Canaveral, Port Canaveral, Kennedy Space Center, and the Florida Space Coast.",
    },
    {
      question: "Do you offer sunset cruises near Cocoa Beach?",
      answer: "Yes. We offer private and small-group sunset cruises from Merritt Island on the Indian River Lagoon, close to Cocoa Beach, Cape Canaveral, and Port Canaveral.",
    },
    {
      question: "Can we watch a rocket launch from the boat?",
      answer: "Launch-day departures may be available when schedules and conditions line up. Contact Dolphin Island Tours before booking if rocket launch viewing is your main goal.",
    },
    {
      question: "How many guests are on each tour?",
      answer: "Tours are small-group experiences for 3 to 6 guests per boat.",
    },
    {
      question: "What should I bring?",
      answer: "Sunscreen, hat, sunglasses, water, a light layer, and your camera. Closed-toe shoes recommended.",
    },
    {
      question: "What if the weather is bad?",
      answer: "If we have to cancel for weather we'll reschedule or refund in full - no questions.",
    },
    {
      question: "Are kids welcome?",
      answer: "Absolutely. Life jackets in all sizes provided. Best for ages 4+.",
    },
    {
      question: "Can we charter privately?",
      answer: "Yes - the boat is yours for 3-6 guests on every tour. No strangers.",
    },
    {
      question: "Where do we meet?",
      answer: "2700 Harbor Town Drive, Merritt Island, FL 32952. Arrive 15 minutes before departure.",
    },
  ],
  navigation: {
    header: [
      { label: "Tours", url: "/tours", visibility: "all" },
      { label: "Reviews", url: "/reviews", visibility: "all" },
      { label: "Find Booking", url: "/find-booking", visibility: "all" },
      { label: "About", url: "/about", visibility: "all" },
      { label: "Contact", url: "/contact", visibility: "all" },
    ],
    footer: [
      { label: "Book a Tour", url: "/tours", visibility: "all" },
      { label: "Find Booking", url: "/find-booking", visibility: "all" },
      { label: "About Us", url: "/about", visibility: "all" },
      { label: "FAQs", url: "/#faq", visibility: "all" },
      { label: "Contact", url: "/contact", visibility: "all" },
    ],
  },
};

export const DEFAULT_PAGES = {
  home: {
    seo_title: "Private Merritt Island Dolphin Tours | Cocoa Beach Boat Tours",
    seo_description: "Book a private or small-group Merritt Island dolphin tour with Dolphin Island Tours LLC near Cocoa Beach, Cape Canaveral, Port Canaveral, Kennedy Space Center, and the Indian River Lagoon. Choose dolphin watching, manatee and wildlife viewing, sunset cruises, rocket launch viewing, family sightseeing, couples trips, and custom Space Coast boat tours from Harbortown Marina.",
    seo_keywords: HOME_SEO_KEYWORDS,
    hero_eyebrow: "Merritt Island · Cocoa Beach · Space Coast, FL",
    hero_title: "Merritt Island Dolphin Tours & Sunset Cruises",
    hero_subtitle: "Private and small-group boat tours near Cocoa Beach for dolphin watching, manatees, sunset cruises, and rocket launch viewing on the Indian River Lagoon.",
    hero_image_url: "/images/hero-ocean.jpg",
    primary_button_label: "Book a tour",
    primary_button_url: "/tours",
    secondary_button_label: "What you'll see",
    secondary_button_url: "#highlights",
    intro_eyebrow: "What you'll see",
    intro_title: "A personal Space Coast boat tour built around your group.",
    section_one_title: "Book a Merritt Island boat tour.",
    section_two_title: "Guest reviews.",
    cta_title: "At the Harbortown marina.",
    cta_body: "Tours leave on time - arrive 15 minutes early.",
  },
  tours: {
    seo_title: "Private Merritt Island Boat Tours | Dolphin, Sunset & Launch",
    seo_description: "Compare Merritt Island boat tours for dolphins, manatees, sunset cruises, private trips, and rocket launch viewing.",
    seo_keywords: TOURS_SEO_KEYWORDS,
    hero_eyebrow: "Pick your trip",
    hero_title: "Merritt Island boat tours",
    hero_subtitle: "Dolphin, manatee, wildlife, sunset, and rocket launch trips near Cocoa Beach. Private and small-group tours on the Indian River Lagoon.",
    hero_image_url: "/images/sunset-water.jpg",
  },
  about: {
    seo_title: "About Dolphin Island Tours | Private Space Coast Boat Tours",
    seo_description: "Meet Dolphin Island Tours, a locally owned Merritt Island boat tour company offering personal dolphin, sunset, wildlife, and launch trips.",
    seo_keywords: ABOUT_SEO_KEYWORDS,
    hero_eyebrow: "About us",
    hero_title: "About Dolphin Island Tours",
    hero_image_url: "/images/boat.jpg",
    intro_title: "Welcome aboard.",
    intro_body: "Welcome to Dolphin Island Tours, where unforgettable memories meet the beauty of Florida's coastline. Based in Merritt Island, we created our dolphin tour company from a love of the water, wildlife, and sharing the natural beauty of the Space Coast with others.\n\nWhat started as a dream quickly became a mission to give families, couples, and visitors a relaxing and exciting way to experience dolphins in their natural habitat.\n\nOur tours are designed to feel personal, private, welcoming, and authentic. Whether you're spotting playful dolphins, enjoying a breathtaking sunset, planning an exclusive family trip, or simply relaxing on the water, we want every guest to leave with memories they'll never forget.\n\nWe are proud to be locally owned and operated, and we can't wait to welcome you aboard.",
    section_one_title: "Personal, private, and authentic.",
    section_one_body: "Every trip is built around small groups, local knowledge, and a relaxed Space Coast experience with no crowded tour boat feel.",
  },
  contact: {
    seo_title: "Contact Dolphin Island Tours | Private Boat Tour Questions",
    seo_description: "Contact Dolphin Island Tours for private Merritt Island boat tours, dolphin trips, sunset cruises, launch viewing, and custom requests.",
    seo_keywords: CONTACT_SEO_KEYWORDS,
    hero_eyebrow: "Get in touch",
    hero_title: "Questions about a private or custom boat tour?",
    hero_image_url: "/images/lagoon.jpg",
    section_one_title: "Reach us directly",
    section_one_body: "Ask about private tours, exclusive trips, custom timing, onboard preferences, celebrations, wildlife tours, sunset cruises, and rocket launch viewing.",
    section_two_title: "Send a message",
    cta_title: "Thanks - we got it.",
    cta_body: "Check your inbox for a confirmation. We'll reply within one business day.",
  },
  reviews: {
    seo_title: "Dolphin Island Tours Reviews | Merritt Island Boat Tours",
    seo_description: "Read Google reviews for Dolphin Island Tours LLC and share your own public Google review after a Merritt Island dolphin tour, sunset cruise, wildlife trip, rocket launch viewing tour, or private Space Coast boat tour near Cocoa Beach and Cape Canaveral.",
    seo_keywords: REVIEWS_SEO_KEYWORDS,
  },
  book: {
    seo_title: "Book a Tour | Dolphin Island Tours",
    seo_description: "Book a Dolphin Island Tours boat tour.",
    seo_keywords: BOOK_SEO_KEYWORDS,
  },
  find_booking: {
    seo_title: "Find My Booking | Dolphin Island Tours",
    seo_description: "Find your Dolphin Island Tours booking with your email and last name, then download your confirmation receipt.",
    seo_keywords: FIND_BOOKING_SEO_KEYWORDS,
  },
};

export function pageKeyFromPath(pathname) {
  if (pathname === "/") return "home";
  if (pathname.startsWith("/find-booking")) return "find_booking";
  if (pathname.startsWith("/book")) return "book";
  if (pathname.startsWith("/tours")) return "tours";
  if (pathname.startsWith("/reviews")) return "reviews";
  if (pathname.startsWith("/about")) return "about";
  if (pathname.startsWith("/contact")) return "contact";
  return "";
}
