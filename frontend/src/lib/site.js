import { useEffect, useMemo, useState } from "react";
import { api } from "./api.js";
import { DEFAULT_PAGES, DEFAULT_SETTINGS, pageKeyFromPath } from "./siteData.js";

export { DEFAULT_SETTINGS, pageKeyFromPath };

let siteCache = DEFAULT_SETTINGS;
let sitePromise = null;

export function primeSite(initialSite) {
  if (initialSite) siteCache = { ...DEFAULT_SETTINGS, ...initialSite };
}

function absolutize(src) {
  if (!src) return src;
  if (src.startsWith("http")) return src;
  return src;
}

export function imageFrom(settings, key, fallback) {
  return absolutize(settings?.images?.[key]?.image_url || fallback);
}

function loadSite() {
  if (!sitePromise) {
    sitePromise = api.site()
      .then((data) => {
        siteCache = { ...DEFAULT_SETTINGS, ...data };
        return siteCache;
      })
      .catch((error) => {
        sitePromise = null;
        throw error;
      });
  }
  return sitePromise;
}

export function preloadSite() {
  return loadSite().catch(() => DEFAULT_SETTINGS);
}

export function useSite(pageKey) {
  const [site, setSite] = useState(siteCache);

  useEffect(() => {
    let alive = true;
    loadSite().then((data) => {
      if (alive) setSite(data);
    }).catch(() => {});
    return () => { alive = false; };
  }, []);

  return useMemo(() => {
    const page = { ...(DEFAULT_PAGES[pageKey] || {}), ...(site.pages?.[pageKey] || {}) };
    return { site, page };
  }, [site, pageKey]);
}
