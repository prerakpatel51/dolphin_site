export const DEFAULT_SETTINGS = {
  site_name: "Dolphin Island Tours",
  tagline: "Creating unforgettable dolphin encounters on Florida's Space Coast.",
  seo_title: "Dolphin Island Tours | Private Merritt Island Boat Tours",
  seo_description: "Book private and small-group Merritt Island dolphin tours, sunset cruises, wildlife trips, and rocket launch boat tours near Cocoa Beach.",
  seo_keywords: "Merritt Island dolphin tours, private boat tour Cocoa Beach, exclusive boat tours, Cape Canaveral rocket launch boat tour, Indian River Lagoon, sunset cruise, manatee tour",
  contact_email: "lauren@dolphinislandtours.com",
  contact_phone: "321-390-0176",
  address: "2700 Harbor Town Drive, Merritt Island, FL 32952",
  meeting_instructions: "Arrive 15 minutes before departure.",
  hours: "Open daily 9 AM - 5 PM",
  maps_url: "https://maps.google.com/?q=2700+Harbor+Town+Drive+Merritt+Island+FL+32952",
  map_embed_url: "https://www.google.com/maps?q=2700+Harbor+Town+Drive+Merritt+Island+FL+32952&output=embed",
  price_blurb: "$60 per person · 3-6 guests",
  review_count: 0,
  average_rating: "0.0",
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
      { label: "About", url: "/about", visibility: "all" },
      { label: "Contact", url: "/contact", visibility: "all" },
      { label: "My Bookings", url: "/bookings", visibility: "authenticated" },
      { label: "Account", url: "/account", visibility: "authenticated" },
      { label: "Login", url: "/login", visibility: "anonymous" },
      { label: "Sign up", url: "/signup", visibility: "anonymous", is_button: true },
    ],
    footer: [
      { label: "Book a Tour", url: "/tours", visibility: "all" },
      { label: "About Us", url: "/about", visibility: "all" },
      { label: "FAQs", url: "/#faq", visibility: "all" },
      { label: "Contact", url: "/contact", visibility: "all" },
    ],
  },
};

export const DEFAULT_PAGES = {
  home: {
    seo_title: "Private Merritt Island Dolphin Tours | Cocoa Beach Boat Tours",
    seo_description: "Book private and small-group Merritt Island dolphin tours, sunset cruises, wildlife trips, and rocket launch boat tours near Cocoa Beach.",
    seo_keywords: "Merritt Island dolphin tours, private boat tour Cocoa Beach, exclusive boat tours, Cape Canaveral rocket launch boat tour, Indian River Lagoon, sunset cruise, manatee tour",
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
    seo_keywords: "private Merritt Island boat tours, exclusive boat tours, Cocoa Beach boat tour, dolphin wildlife excursion, sunset cruise, manatee tour, rocket launch boat",
    hero_eyebrow: "Pick your trip",
    hero_title: "Merritt Island boat tours",
    hero_subtitle: "Dolphin, manatee, wildlife, sunset, and rocket launch trips near Cocoa Beach. Private and small-group tours on the Indian River Lagoon.",
    hero_image_url: "/images/sunset-water.jpg",
  },
  about: {
    seo_title: "About Dolphin Island Tours | Private Space Coast Boat Tours",
    seo_description: "Meet Dolphin Island Tours, a locally owned Merritt Island boat tour company offering personal dolphin, sunset, wildlife, and launch trips.",
    seo_keywords: "private Space Coast boat tours, local Merritt Island captain, Cocoa Beach dolphin tour company, Indian River Lagoon guide, exclusive boat tour",
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
    seo_keywords: "contact private boat tour, Merritt Island dolphin tour phone, Cocoa Beach private charter, exclusive boat tour questions, rocket launch boat booking",
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
    seo_description: "Read verified guest reviews for Merritt Island dolphin tours, sunset cruises, wildlife trips, and Space Coast boat tours.",
  },
  book: {
    seo_title: "Book a Tour | Dolphin Island Tours",
    seo_description: "Book a Dolphin Island Tours boat tour.",
  },
  account: {
    seo_title: "Account | Dolphin Island Tours",
    seo_description: "Manage your Dolphin Island Tours account details and marketing email preferences.",
  },
  bookings: {
    seo_title: "My Bookings | Dolphin Island Tours",
    seo_description: "Review your Dolphin Island Tours bookings and receipts.",
  },
  login: {
    seo_title: "Login | Dolphin Island Tours",
    seo_description: "Log in to your Dolphin Island Tours account.",
  },
  signup: {
    seo_title: "Sign Up | Dolphin Island Tours",
    seo_description: "Create a Dolphin Island Tours account.",
  },
  forgot_password: {
    seo_title: "Forgot Password | Dolphin Island Tours",
  },
  reset_password: {
    seo_title: "Reset Password | Dolphin Island Tours",
  },
};

export function pageKeyFromPath(pathname) {
  if (pathname === "/") return "home";
  if (pathname.startsWith("/book")) return "book";
  if (pathname.startsWith("/tours")) return "tours";
  if (pathname.startsWith("/reviews")) return "reviews";
  if (pathname.startsWith("/about")) return "about";
  if (pathname.startsWith("/contact")) return "contact";
  if (pathname.startsWith("/login")) return "login";
  if (pathname.startsWith("/signup")) return "signup";
  if (pathname.startsWith("/account")) return "account";
  if (pathname.startsWith("/bookings")) return "bookings";
  if (pathname.startsWith("/forgot-password")) return "forgot_password";
  if (pathname.startsWith("/reset-password")) return "reset_password";
  return "";
}
