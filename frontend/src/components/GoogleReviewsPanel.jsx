import { DEFAULT_GOOGLE_BUSINESS_URL, DEFAULT_GOOGLE_REVIEW_URL, DEFAULT_GOOGLE_REVIEWS_EMBED_URL, DEFAULT_GOOGLE_REVIEWS_URL } from "../lib/siteData.js";
import { Stars } from "./Stars.jsx";

export function googleReviewLinks(site = {}) {
  const businessUrl = site.google_business_url || DEFAULT_GOOGLE_BUSINESS_URL;
  const reviewsUrl = site.google_reviews_url || businessUrl || DEFAULT_GOOGLE_REVIEWS_URL;
  return {
    businessUrl,
    reviewsUrl,
    reviewUrl: site.google_review_url || reviewsUrl || DEFAULT_GOOGLE_REVIEW_URL,
    embedUrl: site.google_reviews_embed_url || site.map_embed_url || DEFAULT_GOOGLE_REVIEWS_EMBED_URL,
  };
}

export default function GoogleReviewsPanel({ site, className = "", compact = false }) {
  const { businessUrl, reviewsUrl, reviewUrl, embedUrl } = googleReviewLinks(site);
  const averageRating = Number(site?.average_rating || 5);
  const reviewCount = Number(site?.review_count || 0);
  const reviewLabel = reviewCount > 0
    ? `${reviewCount} Google review${reviewCount !== 1 ? "s" : ""}`
    : "Google reviews";

  return (
    <div className={`grid lg:grid-cols-[minmax(0,0.85fr)_minmax(0,1.15fr)] gap-6 ${className}`}>
      <div className="card p-6 sm:p-8 bg-white">
        <p className="uppercase tracking-[0.3em] text-ocean-500 text-xs mb-3">Google reviews</p>
        <div className="flex flex-wrap items-center gap-3">
          <Stars value={averageRating} size={24} />
          <span className="text-3xl font-display text-ocean-950">{averageRating.toFixed(1)}</span>
        </div>
        <p className="mt-2 text-ocean-700">{reviewLabel}</p>
        <h2 className={`${compact ? "text-2xl" : "text-3xl sm:text-4xl"} mt-6 font-display`}>
          Reviews live on Google.
        </h2>
        <p className="mt-3 text-ocean-700 leading-relaxed">
          Read public Google reviews for Dolphin Island Tours LLC or leave your own review on Google. No Dolphin Island Tours account is required.
        </p>
        <div className="mt-6 flex flex-col sm:flex-row sm:flex-wrap gap-3">
          <a className="btn-primary text-center" href={reviewUrl} target="_blank" rel="noreferrer">
            Add a Google review
          </a>
          <a className="btn-ghost text-center" href={reviewsUrl} target="_blank" rel="noreferrer">
            View Google reviews
          </a>
          <a className="text-sm font-semibold text-ocean-700 hover:text-ocean-900 underline underline-offset-4 sm:self-center" href={businessUrl} target="_blank" rel="noreferrer">
            Open Google Business Profile
          </a>
        </div>
      </div>
      <div className="rounded-2xl overflow-hidden shadow-xl border border-ocean-100 bg-ocean-100 min-h-[360px]">
        <iframe
          title="Dolphin Island Tours Google reviews and map"
          src={embedUrl}
          className="w-full h-full min-h-[360px]"
          loading="lazy"
          referrerPolicy="no-referrer-when-downgrade"
        />
      </div>
    </div>
  );
}
