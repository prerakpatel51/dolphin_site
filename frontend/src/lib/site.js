import { useEffect, useMemo, useState } from "react";
import { api } from "./api.js";
import { DEFAULT_PAGES, DEFAULT_SETTINGS, pageKeyFromPath } from "./siteData.js";

export { DEFAULT_SETTINGS, pageKeyFromPath };

let siteCache = DEFAULT_SETTINGS;
let sitePromise = null;

export function primeSite(initialSite) {
  if (typeof window !== "undefined" && initialSite) {
    siteCache = { ...DEFAULT_SETTINGS, ...initialSite };
  }
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

export function useSite(pageKey, initialSite = null) {
  const [site, setSite] = useState(() => {
    if (initialSite) return { ...DEFAULT_SETTINGS, ...initialSite };
    if (typeof window === "undefined") return DEFAULT_SETTINGS;
    return siteCache;
  });

  useEffect(() => {
    let alive = true;
    if (initialSite) {
      siteCache = { ...DEFAULT_SETTINGS, ...initialSite };
      setSite(siteCache);
    }
    loadSite().then((data) => {
      if (alive) setSite(data);
    }).catch(() => {});
    return () => { alive = false; };
  }, [initialSite]);

  return useMemo(() => {
    const page = { ...(DEFAULT_PAGES[pageKey] || {}), ...(site.pages?.[pageKey] || {}) };
    return { site, page };
  }, [site, pageKey]);
}
