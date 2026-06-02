import { DEFAULT_SETTINGS, pageKeyFromPath } from "./siteData.js";

const PUBLIC_SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || "https://dolphinsite-production.up.railway.app";
const RAW_API_BASE = process.env.INTERNAL_API_BASE || process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000/api";

function apiBase() {
  if (RAW_API_BASE.startsWith("http")) return RAW_API_BASE;
  if (RAW_API_BASE.startsWith("/")) return `${PUBLIC_SITE_URL}${RAW_API_BASE}`;
  return RAW_API_BASE;
}

async function getJson(path, revalidate = 300) {
  try {
    const site = new URL(PUBLIC_SITE_URL);
    const cacheOptions = revalidate === 0 ? { cache: "no-store" } : { next: { revalidate } };
    const response = await fetch(`${apiBase()}${path}`, {
      headers: {
        host: site.host,
        origin: site.origin,
        referer: `${site.origin}/`,
        "x-forwarded-host": site.host,
        "x-forwarded-proto": site.protocol.replace(":", ""),
      },
      ...cacheOptions,
      signal: AbortSignal.timeout(5000),
    });
    if (!response.ok) return null;
    return response.json();
  } catch {
    return null;
  }
}

export async function getSite() {
  const site = await getJson("/site/", 0);
  return { ...DEFAULT_SETTINGS, ...(site || {}) };
}

export async function getTours() {
  const tours = await getJson("/tours/");
  return tours?.results || tours || [];
}

export async function getTour(slug) {
  return getJson(`/tours/${slug}/`);
}

export async function getTourDates(slug) {
  const dates = await getJson(`/tours/${slug}/dates/`);
  return dates?.dates || {};
}

export async function getReviews(params = {}) {
  const query = new URLSearchParams(params).toString();
  const reviews = await getJson(`/reviews/${query ? `?${query}` : ""}`);
  return reviews?.results || reviews || [];
}

export async function getAllReviewStats() {
  return await getJson("/reviews/stats/") || { count: 0, average: 0 };
}

export async function metadataForPath(pathname, overrides = {}) {
  const site = await getSite();
  const pageKey = pageKeyFromPath(pathname);
  const page = { ...(site.pages?.[pageKey] || {}) };
  const title = overrides.title || page.seo_title || site.seo_title;
  const description = overrides.description || page.seo_description || site.seo_description;
  const image = overrides.image || page.hero_image_url || site.images?.og_default?.image_url || "/images/hero-ocean.jpg";
  const canonical = `${PUBLIC_SITE_URL}${pathname === "/" ? "" : pathname}`;

  return {
    title,
    description,
    keywords: overrides.keywords || page.seo_keywords || site.seo_keywords,
    alternates: { canonical },
    openGraph: {
      title,
      description,
      url: canonical,
      siteName: site.site_name,
      type: ["article", "book", "profile", "website"].includes(overrides.type) ? overrides.type : "website",
      images: image ? [{ url: image.startsWith("http") ? image : `${PUBLIC_SITE_URL}${image}` }] : undefined,
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
      images: image ? [image.startsWith("http") ? image : `${PUBLIC_SITE_URL}${image}`] : undefined,
    },
    robots: overrides.robots || "index, follow, max-image-preview:large",
  };
}
