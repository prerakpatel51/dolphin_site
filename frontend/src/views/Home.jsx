"use client";

import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import { api } from "../lib/api.js";
import { imageFrom, useSite } from "../lib/site.js";
import { breadcrumbJsonLd, faqJsonLd, graphJsonLd, localBusinessJsonLd, originUrl, websiteJsonLd } from "../lib/seo.js";
import SEO from "../components/SEO.jsx";
import GoogleReviewsPanel from "../components/GoogleReviewsPanel.jsx";

const HIGHLIGHTS = [
  { img: "/images/dolphin.jpg", title: "Private dolphin tours", body: "Cruise with only 3 to 6 guests, giving your family, couple, or exclusive group a personal Merritt Island dolphin tour." },
  { img: "/images/manatee.jpg", title: "Manatees & lagoon wildlife", body: "Look for manatees, ospreys, roseate spoonbills, pelicans, and Indian River Lagoon wildlife near Cocoa Beach and Cape Canaveral." },
  { img: "/images/rocket.jpg", title: "Rocket launch boat tours", body: "On launch days, the lagoon can be an incredible place to watch. Ask about private launch-day departures near Cape Canaveral." },
];

export default function Home({ initialSite, initialTours = [] }) {
  const [tours, setTours] = useState(initialTours);
  const { site, page } = useSite("home", initialSite);
  useEffect(() => {
    let alive = true;
    api.tours().then((result) => {
      if (!alive) return;
      setTours(result.results || result);
    }).catch(() => {});
    return () => { alive = false; };
  }, []);

  const heroImage = page.hero_image_url || imageFrom(site, "hero", "/images/hero-ocean.jpg");
  const googleReviewCount = Number(site.review_count || 0);
  const averageRating = Number(site.average_rating || 5);
  const siteWithReviewStats = {
    ...site,
    review_count: googleReviewCount,
    average_rating: averageRating.toFixed(1),
  };
  const priceParts = String(site.price_blurb || "$60 per person").split("·").map(part => part.trim()).filter(Boolean);
  const primaryPrice = priceParts[0] || "$60 per person";
  const [priceValue, ...priceLabelParts] = primaryPrice.split(/\s+/);
  const priceLabel = priceLabelParts.join(" ") || "per person";
  const reviewsHeading = googleReviewCount > 0
    ? `${averageRating.toFixed(1)} stars on Google.`
    : "Google reviews.";
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
  const faqs = (site.faqs || []).map(faq => [faq.question, faq.answer]).filter(([question, answer]) => question && answer);

  return (
    <div>
      <SEO
        title={page.seo_title || site.seo_title}
        description={page.seo_description || site.seo_description}
        keywords={page.seo_keywords || site.seo_keywords}
        image={heroImage}
        canonical="/"
        jsonLd={graphJsonLd([
          localBusinessJsonLd(siteWithReviewStats, heroImage),
          websiteJsonLd(siteWithReviewStats),
          breadcrumbJsonLd([{ name: "Home", path: "/" }]),
          faqs.length > 0 ? faqJsonLd(faqs) : null,
          {
            "@type": "ItemList",
            "name": "Dolphin Island Tours boat tour options",
            "itemListElement": tours.map((tour, index) => ({
              "@type": "ListItem",
              "position": index + 1,
              "url": `${originUrl()}/tours/${tour.slug}`,
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
          <h1 className="mt-5 sm:mt-6 text-[2.65rem] sm:text-5xl lg:text-7xl font-display max-w-4xl leading-[1.03]">
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
            {googleReviewCount > 0 ? (
              <>
                <Stat k={averageRating.toFixed(1)} v="average rating" />
                <Stat k={String(googleReviewCount)} v={`Google review${googleReviewCount !== 1 ? "s" : ""}`} />
              </>
            ) : (
              <Stat k="Google" v="reviews" />
            )}
            <Stat k="2010" v="locally owned" />
            <Stat k="6" v="max guests" />
            <Stat k={priceValue} v={priceLabel} />
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
            "We started Dolphin Island Tours so visitors could really see the Space Coast - personally, privately, and the way the locals do."
          </p>
          <p className="mt-6 text-ocean-200">— Lewis, Captain &amp; Founder · Lauren, Founder</p>
          <Link to="/about" className="btn-ghost mt-8 inline-flex">Our story →</Link>
        </div>
      </section>

      {/* TESTIMONIALS */}
      <section className="max-w-6xl mx-auto px-4 py-16 sm:py-24">
        <div className="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-6 mb-8">
          <div>
            <p className="uppercase tracking-[0.3em] text-ocean-500 text-xs mb-3">Guest stories</p>
            <h2 className="text-3xl sm:text-5xl">{reviewsHeading}</h2>
          </div>
        </div>
        <GoogleReviewsPanel site={site} compact />
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
      <section id="faq" className="bg-white py-16 sm:py-24 scroll-mt-24">
        <div className="max-w-3xl mx-auto px-4">
          <div className="text-center mb-12">
            <p className="uppercase tracking-[0.3em] text-ocean-500 text-xs mb-3">Good to know</p>
            <h2 className="text-3xl sm:text-5xl">Frequently asked.</h2>
          </div>
          <div className="space-y-3">
            {faqs.map(([q, a]) => (
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
            {page.cta_body && <p className="text-ocean-700 mt-3">{page.cta_body}</p>}
            <p className="text-ocean-700 mt-3">{site.hours}. {site.meeting_instructions}</p>
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
