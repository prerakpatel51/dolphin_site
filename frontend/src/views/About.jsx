"use client";

import SEO from "../components/SEO.jsx";
import { imageFrom, useSite } from "../lib/site.js";
import { breadcrumbJsonLd, graphJsonLd, localBusinessJsonLd } from "../lib/seo.js";

export default function About() {
  const { site, page } = useSite("about");
  const heroImage = page.hero_image_url || imageFrom(site, "about", "/images/boat.jpg");
  const aboutSecondary = imageFrom(site, "about_secondary", "/images/welcome.jpg");
  const lagoon = imageFrom(site, "story", "/images/lagoon.jpg");

  return (
    <div>
      <SEO
        title={page.seo_title || "About - Dolphin Island Tours"}
        description={page.seo_description}
        keywords={page.seo_keywords}
        image={heroImage}
        canonical="/about"
        jsonLd={graphJsonLd([
          localBusinessJsonLd(site, heroImage),
          breadcrumbJsonLd([{ name: "Home", path: "/" }, { name: "About", path: "/about" }]),
        ])}
      />
      <section className="relative h-[40vh] min-h-[260px] overflow-hidden">
        <img src={heroImage} alt="" fetchPriority="high" className="absolute inset-0 w-full h-full object-cover" />
        <div className="absolute inset-0 bg-ocean-950/60" />
        <div className="relative max-w-4xl mx-auto px-4 h-full flex flex-col justify-end pb-8 sm:pb-12">
          <p className="uppercase tracking-[0.25em] sm:tracking-[0.3em] text-ocean-200 text-[10px] sm:text-xs mb-2 sm:mb-3">{page.hero_eyebrow}</p>
          <h1 className="text-4xl sm:text-6xl text-white font-display leading-[1.05]">{page.hero_title}</h1>
        </div>
      </section>

      <div className="max-w-3xl mx-auto px-4 py-10 sm:py-16">
        {page.intro_eyebrow && <p className="uppercase tracking-[0.24em] text-ocean-500 text-xs mb-3">{page.intro_eyebrow}</p>}
        {page.intro_title && <h2 className="text-3xl sm:text-4xl mb-4">{page.intro_title}</h2>}
        <p className="text-lg sm:text-xl text-ocean-800 leading-relaxed whitespace-pre-line">
          {page.intro_body}
        </p>

        <div className="grid sm:grid-cols-2 gap-4 my-12">
          <img src={aboutSecondary} alt="" loading="lazy" decoding="async" className="rounded-3xl w-full aspect-[4/3] object-cover border border-ocean-100" />
          <img src={lagoon} alt="" loading="lazy" decoding="async" className="rounded-3xl w-full aspect-[4/3] object-cover border border-ocean-100" />
        </div>

        <h2 className="text-3xl mt-10 mb-4">{page.section_one_title}</h2>
        {page.section_one_body && <p className="text-ocean-700 mb-5">{page.section_one_body}</p>}
        <ul className="space-y-3">
          {[
            ["Wildlife first", "We keep a respectful distance and follow NOAA marine mammal guidelines on every dolphin, manatee, and wildlife tour."],
            ["Private-style trips", "Maximum six guests per tour means no crowded boat, no strangers if your group fills the trip, and more time on the water."],
            ["Custom requests", "Ask about private tours, exclusive trips, celebrations, custom timing, and onboard preferences before booking."],
            ["Local roots", "We support Brevard County conservation partners and share real Space Coast knowledge from Merritt Island to Cocoa Beach and Cape Canaveral."],
          ].map(([t, b]) => (
            <li key={t} className="card p-5">
              <h3 className="text-lg font-semibold mb-1">{t}</h3>
              <p className="text-ocean-700">{b}</p>
            </li>
          ))}
        </ul>
        {(page.section_two_title || page.section_two_body) && (
          <div className="mt-12 border-t border-ocean-100 pt-8">
            {page.section_two_title && <h2 className="text-3xl mb-4">{page.section_two_title}</h2>}
            {page.section_two_body && <p className="text-lg text-ocean-800 leading-relaxed whitespace-pre-line">{page.section_two_body}</p>}
          </div>
        )}
      </div>
    </div>
  );
}
