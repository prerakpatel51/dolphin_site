import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import { api } from "../lib/api.js";
import { imageFrom, useSite } from "../lib/site.js";
import { breadcrumbJsonLd, faqJsonLd, graphJsonLd, homeFaq, localBusinessJsonLd, websiteJsonLd } from "../lib/seo.js";
import { useAuth } from "../lib/auth.jsx";
import SEO from "../components/SEO.jsx";
import { Stars } from "../components/Stars.jsx";

const HIGHLIGHTS = [
  { img: "/images/dolphin.jpg", title: "Wild dolphins", body: "Bottlenose dolphins ride the boat's wake almost every trip — a quiet thrill you'll remember for years." },
  { img: "/images/manatee.jpg", title: "Manatees & birds", body: "Gentle manatees, ospreys, roseate spoonbills, and pelicans live throughout the Indian River Lagoon." },
  { img: "/images/rocket.jpg", title: "Rocket launches", body: "On launch days, the lagoon is the best seat in the house. Ask about our launch-day departures." },
];

const FAQ = [
  ...homeFaq,
  ["What should I bring?", "Sunscreen, hat, sunglasses, water, a light layer, and your camera. Closed-toe shoes recommended."],
  ["What if the weather is bad?", "If we have to cancel for weather we'll reschedule or refund in full — no questions."],
  ["Are kids welcome?", "Absolutely. Life jackets in all sizes provided. Best for ages 4+."],
  ["Can we charter privately?", "Yes — the boat is yours for 3–6 guests on every tour. No strangers."],
  ["Where do we meet?", "2700 Harbortown Drive, Merritt Island, FL. Arrive 15 minutes before departure."],
];

export default function Home() {
  const [tours, setTours] = useState([]);
  const [homeReviews, setHomeReviews] = useState([]);
  const [reviewableTours, setReviewableTours] = useState([]);
  const { user } = useAuth();
  const { site, page } = useSite("home");
  useEffect(() => {
    let alive = true;
    Promise.allSettled([
      api.tours(),
      api.reviews({ featured: 1 }),
    ]).then(([tourResult, reviewResult]) => {
      if (!alive) return;
      if (tourResult.status === "fulfilled") setTours(tourResult.value.results || tourResult.value);
      if (reviewResult.status === "fulfilled") {
        const featured = reviewResult.value.results || reviewResult.value;
        if (featured.length > 0) {
          setHomeReviews(featured);
        } else {
          api.reviews().then(d => {
            if (alive) setHomeReviews((d.results || d).slice(0, 3));
          }).catch(() => {});
        }
      }
    });
    return () => { alive = false; };
  }, []);

  useEffect(() => {
    let alive = true;
    if (!user) {
      setReviewableTours([]);
      return () => { alive = false; };
    }
    api.myBookings().then(d => {
      if (!alive) return;
      const unique = new Map();
      (d.results || d)
        .filter(b => b.status === "paid" && b.slot?.tour?.slug)
        .forEach(b => unique.set(b.slot.tour.slug, b.slot.tour));
      setReviewableTours([...unique.values()]);
    }).catch(() => {
      if (alive) setReviewableTours([]);
    });
    return () => { alive = false; };
  }, [user]);
  const heroImage = page.hero_image_url || imageFrom(site, "hero", "/images/hero-ocean.jpg");
  const storyImage = imageFrom(site, "story", "/images/lagoon.jpg");
  const gallery = [
    imageFrom(site, "gallery_1", "/images/dolphin.jpg"),
    imageFrom(site, "gallery_2", "/images/sunset.jpg"),
    imageFrom(site, "gallery_3", "/images/manatee.jpg"),
    imageFrom(site, "gallery_4", "/images/boat.jpg"),
    imageFrom(site, "gallery_5", "/images/sunset-water.jpg"),
    imageFrom(site, "gallery_6", "/images/lagoon.jpg"),
    imageFrom(site, "gallery_7", "/images/welcome.jpg"),
    imageFrom(site, "gallery_8", "/images/rocket.jpg"),
  ];

  return (
    <div>
      <SEO
        title={page.seo_title || site.seo_title}
        description={page.seo_description || site.seo_description}
        keywords={page.seo_keywords || site.seo_keywords}
        image={heroImage}
        canonical="/"
        jsonLd={graphJsonLd([
          localBusinessJsonLd(site, heroImage),
          websiteJsonLd(site),
          breadcrumbJsonLd([{ name: "Home", path: "/" }]),
          faqJsonLd(FAQ),
          {
            "@type": "ItemList",
            "name": "Dolphin Island Tours boat tour options",
            "itemListElement": tours.map((tour, index) => ({
              "@type": "ListItem",
              "position": index + 1,
              "url": `${window.location.origin}/tours/${tour.slug}`,
              "name": tour.name,
            })),
          },
        ])}
      />
      {/* HERO */}
      <section className="relative min-h-[calc(100svh-4rem)] sm:min-h-[680px] overflow-hidden">
        <div className="absolute inset-0">
          <img src={heroImage} alt="" fetchPriority="high" className="w-full h-full object-cover scale-105" />
          <div className="absolute inset-0 bg-gradient-to-br from-ocean-950/90 via-ocean-900/60 to-ocean-900/10" />
          <div className="absolute inset-x-0 bottom-0 h-40 bg-gradient-to-t from-ocean-50 to-transparent" />
        </div>
        <div className="relative max-w-6xl mx-auto px-4 pt-16 pb-16 sm:pt-32 sm:pb-36 text-white">
          <div className="inline-flex items-center gap-2 rounded-full bg-white/10 backdrop-blur border border-white/20 px-3 sm:px-4 py-1.5 text-[10px] sm:text-xs uppercase tracking-[0.2em] sm:tracking-[0.25em] text-ocean-100">
            <span className="w-1.5 h-1.5 rounded-full bg-sand-200 animate-pulse" />
            {page.hero_eyebrow}
          </div>
          <h1 className="mt-5 sm:mt-6 text-[2.65rem] sm:text-6xl lg:text-8xl font-display max-w-4xl leading-[1.02]">
            {page.hero_title}
          </h1>
          <p className="mt-5 sm:mt-7 text-base sm:text-xl text-ocean-100 max-w-2xl leading-relaxed">
            {page.hero_subtitle}
          </p>
          <div className="mt-8 sm:mt-10 flex flex-col sm:flex-row sm:flex-wrap gap-3">
            <Link to={page.primary_button_url || "/tours"} className="btn-primary text-base">{page.primary_button_label || "Book a tour"}</Link>
            <a href={page.secondary_button_url || "#highlights"} className="btn-ghost">{page.secondary_button_label || "What you'll see"}</a>
          </div>
          <div className="mt-10 sm:mt-12 grid grid-cols-2 sm:flex sm:flex-wrap gap-3 sm:gap-x-8 text-sm text-ocean-100">
            <Stat k={`${site.review_count}+`} v="five-star trips" />
            <Stat k="2010" v="locally owned" />
            <Stat k="6" v="max guests" />
            <Stat k="$60" v="per person" />
          </div>
        </div>
      </section>

      {/* HIGHLIGHTS */}
      <section id="highlights" className="max-w-6xl mx-auto px-4 py-14 sm:py-24">
        <div className="text-center mb-14">
          <p className="uppercase tracking-[0.3em] text-ocean-500 text-xs mb-3">{page.intro_eyebrow}</p>
          <h2 className="text-3xl sm:text-5xl">{page.intro_title}</h2>
        </div>
        <div className="grid sm:grid-cols-3 gap-6">
          {HIGHLIGHTS.map(h => (
            <div key={h.title} className="card overflow-hidden group">
              <div className="aspect-[4/3] overflow-hidden">
                <img src={h.img} alt={h.title} loading="lazy" decoding="async" className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-[1.2s]" />
              </div>
              <div className="p-6">
                <div className="h-1 w-10 bg-ocean-400 rounded-full mb-3" />
                <h3 className="text-2xl mb-2">{h.title}</h3>
                <p className="text-ocean-700">{h.body}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* TOURS */}
      <section className="bg-white py-16 sm:py-24">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex flex-wrap items-end justify-between gap-4 mb-12">
            <div>
              <p className="uppercase tracking-[0.3em] text-ocean-500 text-xs mb-3">Pick your trip</p>
              <h2 className="text-3xl sm:text-5xl">{page.section_one_title}</h2>
            </div>
            <Link to="/tours" className="text-ocean-700 hover:text-ocean-900 underline underline-offset-4">All tours →</Link>
          </div>
          <div className="grid md:grid-cols-2 gap-6">
            {tours.slice(0, 2).map(t => (
              <Link key={t.id} to={`/tours/${t.slug}`} className="card overflow-hidden group relative">
                <div className="aspect-[4/3] overflow-hidden bg-ocean-100">
                  <img src={t.image_url || "/images/welcome.jpg"} alt={t.name} loading="lazy" decoding="async" className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-[1.2s]" />
                  <div className="absolute inset-0 bg-gradient-to-t from-ocean-950/60 via-transparent to-transparent" />
                </div>
                <div className="absolute bottom-0 left-0 right-0 p-4 sm:p-6 text-white">
                  <div className="flex flex-wrap items-center gap-x-2 gap-y-1 text-[11px] sm:text-xs uppercase tracking-wider text-ocean-100 mb-2">
                    <span>{t.duration_minutes} min</span><span className="opacity-50">·</span>
                    <span>${t.price_per_person} / person</span><span className="opacity-50">·</span>
                    <span>{t.min_party}-{t.max_party} guests</span>
                  </div>
                  <h3 className="text-2xl sm:text-3xl font-display">{t.name}</h3>
                  <p className="text-ocean-100 mt-2 line-clamp-2 text-sm sm:text-base">{t.short_description}</p>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* STORY STRIP */}
      <section className="relative py-16 sm:py-24 overflow-hidden">
        <img src={storyImage} alt="" loading="lazy" decoding="async" className="absolute inset-0 w-full h-full object-cover" />
        <div className="absolute inset-0 bg-ocean-950/70" />
        <div className="relative max-w-3xl mx-auto px-4 text-center text-white">
          <p className="uppercase tracking-[0.3em] text-ocean-200 text-xs mb-4">Family-owned since 2010</p>
          <p className="text-xl sm:text-3xl font-display leading-snug">
            "We started Dolphin Island Tours so visitors could really see the Space Coast — slowly, quietly, the way the locals do."
          </p>
          <p className="mt-6 text-ocean-200">— Lewis, Captain &amp; Founder</p>
          <Link to="/about" className="btn-ghost mt-8 inline-flex">Our story →</Link>
        </div>
      </section>

      {/* TESTIMONIALS */}
      <section className="max-w-6xl mx-auto px-4 py-16 sm:py-24">
        <div className="text-center mb-12">
          <p className="uppercase tracking-[0.3em] text-ocean-500 text-xs mb-3">Guest stories</p>
          <h2 className="text-3xl sm:text-5xl">{page.section_two_title}</h2>
        </div>
        <div className="grid md:grid-cols-3 gap-6">
          {homeReviews.length === 0 && (
            <div className="card p-7 md:col-span-3 text-center">
              <h3 className="text-xl">Real guest reviews will appear here soon.</h3>
              <p className="text-ocean-700 mt-2">After guests share approved tour reviews, the latest highlights show on the homepage.</p>
            </div>
          )}
          {homeReviews.slice(0, 3).map(r => (
            <div key={r.id} className="card p-7">
              <Stars value={r.rating} size={20} />
              {r.title && <h3 className="text-lg mt-2">{r.title}</h3>}
              <p className="text-ocean-800 leading-relaxed mt-2">"{r.body}"</p>
              <p className="mt-5 text-sm font-semibold text-ocean-900">— {r.author_name}</p>
            </div>
          ))}
        </div>
        {user && reviewableTours.length > 0 && (
          <div className="mt-8 card p-5 sm:p-7 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h3 className="text-2xl">Share your tour experience.</h3>
              <p className="text-ocean-700 text-sm mt-1">Your paid booking lets you leave a verified review for future guests.</p>
            </div>
            <div className="flex flex-wrap gap-2">
              {reviewableTours.map(tour => (
                <Link key={tour.slug} to={`/tours/${tour.slug}#reviews`} className="btn-ghost !py-2 !px-4 text-sm">
                  Review {tour.name}
                </Link>
              ))}
            </div>
          </div>
        )}
      </section>

      {/* GALLERY */}
      <section className="max-w-7xl mx-auto px-4 pb-24">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 sm:gap-3">
          {gallery.map((src, i) => (
            <div key={src} className={`overflow-hidden rounded-xl sm:rounded-2xl ${i % 5 === 0 ? "md:row-span-2 md:col-span-2 aspect-square md:aspect-auto" : "aspect-square"}`}>
              <img src={src} alt="" loading="lazy" decoding="async" className="w-full h-full object-cover hover:scale-105 transition-transform duration-700" />
            </div>
          ))}
        </div>
      </section>

      {/* FAQ */}
      <section className="bg-white py-16 sm:py-24">
        <div className="max-w-3xl mx-auto px-4">
          <div className="text-center mb-12">
            <p className="uppercase tracking-[0.3em] text-ocean-500 text-xs mb-3">Good to know</p>
            <h2 className="text-3xl sm:text-5xl">Frequently asked.</h2>
          </div>
          <div className="space-y-3">
            {FAQ.map(([q, a]) => (
              <details key={q} className="card p-6 group">
                <summary className="cursor-pointer flex justify-between items-center text-lg font-semibold text-ocean-900 list-none">
                  {q}
                  <span className="ml-4 text-ocean-400 group-open:rotate-45 transition-transform text-2xl leading-none">+</span>
                </summary>
                <p className="mt-3 text-ocean-700">{a}</p>
              </details>
            ))}
          </div>
        </div>
      </section>

      {/* MAP / CTA */}
      <section className="bg-ocean-50 py-16 sm:py-24">
        <div className="max-w-6xl mx-auto px-4 grid md:grid-cols-2 gap-12 items-center">
          <div>
            <p className="uppercase tracking-[0.3em] text-ocean-500 text-xs mb-3">Find us</p>
            <h2 className="text-4xl mb-4">{page.cta_title}</h2>
            <p className="text-ocean-700 text-lg">{site.address}</p>
            <p className="text-ocean-700 mt-3">{site.hours}. {page.cta_body || site.meeting_instructions}</p>
            <div className="mt-7 flex flex-wrap gap-3">
              <Link to="/tours" className="btn-primary">Book now</Link>
              <a className="btn-ghost" href={site.maps_url} target="_blank" rel="noreferrer">Open in Maps</a>
            </div>
          </div>
          <div className="rounded-3xl overflow-hidden shadow-2xl aspect-[4/3] border border-ocean-100">
            <iframe
              title="Map"
              src={site.map_embed_url}
              className="w-full h-full"
              loading="lazy"
              referrerPolicy="no-referrer-when-downgrade"
            />
          </div>
        </div>
      </section>
    </div>
  );
}

function Stat({ k, v }) {
  return (
    <div className="rounded-2xl border border-white/15 bg-white/10 px-3 py-2 backdrop-blur-sm sm:border-0 sm:bg-transparent sm:px-0 sm:py-0 flex items-baseline gap-2 min-w-0">
      <span className="text-2xl font-display text-white whitespace-nowrap shrink-0">{k}</span>
      <span className="text-ocean-200 text-sm sm:text-base leading-tight min-w-0">{v}</span>
    </div>
  );
}
