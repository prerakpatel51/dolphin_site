import { useEffect } from "react";

function absoluteUrl(value) {
  if (!value) return "";
  if (value.startsWith("http")) return value;
  return window.location.origin + value;
}

function canonicalUrl(path) {
  if (path) return absoluteUrl(path);
  return window.location.origin + window.location.pathname.replace(/\/$/, "") + (window.location.pathname === "/" ? "/" : "");
}

function setMeta(selector, attr, value) {
  if (!value) return;
  let el = document.querySelector(selector);
  if (!el) {
    el = document.createElement("meta");
    const [, k, v] = selector.match(/\[(\w+)="(.+)"\]/) || [];
    if (k && v) el.setAttribute(k, v);
    document.head.appendChild(el);
  }
  el.setAttribute(attr, value);
}

export default function SEO({ title, description, keywords, image, type = "website", jsonLd, canonical }) {
  useEffect(() => {
    const canonicalHref = canonicalUrl(canonical);
    const absoluteImage = absoluteUrl(image);
    if (title) document.title = title;
    setMeta('meta[name="description"]', "content", description);
    setMeta('meta[name="keywords"]', "content", keywords);
    setMeta('meta[name="robots"]', "content", "index, follow, max-image-preview:large");
    setMeta('meta[property="og:title"]', "content", title);
    setMeta('meta[property="og:description"]', "content", description);
    setMeta('meta[property="og:type"]', "content", type);
    setMeta('meta[property="og:image"]', "content", absoluteImage);
    setMeta('meta[property="og:url"]', "content", canonicalHref);
    setMeta('meta[property="og:site_name"]', "content", "Dolphin Island Tours");
    setMeta('meta[property="og:locale"]', "content", "en_US");
    setMeta('meta[name="twitter:card"]', "content", "summary_large_image");
    setMeta('meta[name="twitter:title"]', "content", title);
    setMeta('meta[name="twitter:description"]', "content", description);
    setMeta('meta[name="twitter:image"]', "content", absoluteImage);

    let link = document.querySelector('link[rel="canonical"]');
    if (!link) { link = document.createElement("link"); link.rel = "canonical"; document.head.appendChild(link); }
    link.href = canonicalHref;

    const id = "page-jsonld";
    let s = document.getElementById(id);
    if (s) s.remove();
    if (jsonLd) {
      s = document.createElement("script");
      s.id = id; s.type = "application/ld+json";
      s.textContent = JSON.stringify(jsonLd);
      document.head.appendChild(s);
    }
  }, [title, description, keywords, image, type, canonical, JSON.stringify(jsonLd)]);
  return null;
}
