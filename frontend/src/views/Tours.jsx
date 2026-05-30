"use client";

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api.js";
import { useSite } from "../lib/site.js";
import { breadcrumbJsonLd, graphJsonLd, localBusinessJsonLd, originUrl } from "../lib/seo.js";
import SEO from "../components/SEO.jsx";

export default function Tours({ initialTours = [] }) {
  const [tours, setTours] = useState(initialTours);
  const { site, page } = useSite("tours");
  useEffect(() => {
    let alive = true;
    api.tours().then(d => {
      if (alive) setTours(d.results || d);
    }).catch(() => {});
    return () => { alive = false; };
  }, []);
  return (
    <div>
      <SEO
        title={page.seo_title || "Tours - Dolphin Island Tours"}
        description={page.seo_description}
        keywords={page.seo_keywords}
        image={page.hero_image_url}
        canonical="/tours"
        jsonLd={graphJsonLd([
          localBusinessJsonLd(site, page.hero_image_url || "/images/sunset-water.jpg"),
          breadcrumbJsonLd([{ name: "Home", path: "/" }, { name: "Tours", path: "/tours" }]),
          {
            "@type": "ItemList",
            "name": "Merritt Island dolphin, wildlife, sunset, and rocket launch boat tours",
            "description": page.seo_description,
            "itemListElement": tours.map((tour, index) => ({
              "@type": "ListItem",
              "position": index + 1,
              "url": `${originUrl()}/tours/${tour.slug}`,
              "name": tour.name,
            })),
          },
        ])}
      />
      <section className="relative h-[35vh] min-h-[260px] overflow-hidden">
        <img src={page.hero_image_url || "/images/sunset-water.jpg"} alt="" fetchPriority="high" className="absolute inset-0 w-full h-full object-cover" />
        <div className="absolute inset-0 bg-ocean-950/55" />
        <div className="relative max-w-6xl mx-auto px-4 h-full flex flex-col justify-end pb-8 sm:pb-10">
          <p className="uppercase tracking-[0.25em] sm:tracking-[0.3em] text-ocean-200 text-[10px] sm:text-xs mb-2 sm:mb-3">{page.hero_eyebrow}</p>
          <h1 className="text-4xl sm:text-6xl text-white font-display">{page.hero_title}</h1>
          <p className="text-ocean-100 mt-2 text-base sm:text-lg max-w-xl">{page.hero_subtitle || site.price_blurb}</p>
        </div>
      </section>
      <div className="max-w-6xl mx-auto px-4 py-10 sm:py-16">
        {Array.isArray(tours) && tours.length > 0 ? (
          <div className="grid sm:grid-cols-2 gap-4 sm:gap-6">
            {tours.map(t => (
              <Link key={t.id} to={`/tours/${t.slug}`} className="card overflow-hidden group relative">
                <div className="aspect-[4/3] overflow-hidden bg-ocean-100">
                  <img src={t.image_url || "/images/welcome.jpg"} alt={t.name} loading="lazy" decoding="async" className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-[1.2s]" />
                  <div className="absolute inset-0 bg-gradient-to-t from-ocean-950/70 via-ocean-950/20 to-transparent" />
                </div>
                <div className="absolute bottom-0 left-0 right-0 p-4 sm:p-6 text-white">
                  <div className="flex flex-wrap items-center gap-x-2 gap-y-1 text-[11px] sm:text-xs uppercase tracking-wider text-ocean-100 mb-2">
                    <span>{t.duration_minutes} min</span><span className="opacity-50">·</span>
                    <span>${t.price_per_person} / person</span><span className="opacity-50">·</span>
                    <span>{t.min_party}-{t.max_party} guests</span>
                  </div>
                  <h2 className="text-2xl sm:text-3xl font-display">{t.name}</h2>
                  <p className="text-ocean-100 mt-2 line-clamp-2 text-sm sm:text-base">{t.short_description}</p>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <div className="text-center py-20">
            <h2 className="text-2xl font-display text-ocean-900">No tours available right now.</h2>
            <p className="text-ocean-600 mt-2">Check back soon or contact us for private charters.</p>
          </div>
        )}
      </div>
    </div>
  );
}
