"use client";

import { Link } from "react-router-dom";
import SEO from "../components/SEO.jsx";
import GoogleReviewsPanel from "../components/GoogleReviewsPanel.jsx";
import { imageFrom, useSite } from "../lib/site.js";

export default function ReviewsPage() {
  const { site, page } = useSite("reviews");
  const heroImage = page.hero_image_url || imageFrom(site, "hero", "/images/hero-ocean.jpg");

  return (
    <div>
      <SEO
        title={page.seo_title || `Google Reviews | ${site.site_name}`}
        description={page.seo_description || site.seo_description}
        keywords={page.seo_keywords || site.seo_keywords}
        image={heroImage}
        canonical="/reviews"
      />

      <section className="bg-white border-b border-ocean-100">
        <div className="max-w-6xl mx-auto px-4 py-12 sm:py-16">
          <p className="uppercase tracking-[0.3em] text-ocean-500 text-xs mb-3">Google reviews</p>
          <div className="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-6">
            <div>
              <h1 className="text-4xl sm:text-6xl font-display">{page.hero_title || "Dolphin Island Tours reviews."}</h1>
              <p className="text-ocean-700 text-lg mt-4 max-w-2xl">
                See Dolphin Island Tours LLC on Google and share a public review after your time on the water.
              </p>
            </div>
            <Link to="/tours" className="btn-primary w-full text-center sm:w-auto">Book a tour</Link>
          </div>
        </div>
      </section>

      <section id="write-review" className="max-w-6xl mx-auto px-4 py-10 sm:py-14 scroll-mt-24">
        <GoogleReviewsPanel site={site} />
      </section>
    </div>
  );
}
