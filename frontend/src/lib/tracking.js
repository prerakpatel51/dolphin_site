function addScript(id, src, inline) {
  if (document.getElementById(id)) return;
  const script = document.createElement("script");
  script.id = id;
  if (src) {
    script.async = true;
    script.src = src;
  }
  if (inline) script.textContent = inline;
  document.head.appendChild(script);
}

export function initMarketingTags(site) {
  if (!site) return;

  if (site.google_tag_manager_id) {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({ "gtm.start": new Date().getTime(), event: "gtm.js" });
    addScript("gtm-script", `https://www.googletagmanager.com/gtm.js?id=${site.google_tag_manager_id}`);
  }

  const googleId = site.google_analytics_id || site.google_ads_id;
  if (googleId) {
    addScript("gtag-script", `https://www.googletagmanager.com/gtag/js?id=${googleId}`);
    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function gtag(){ window.dataLayer.push(arguments); };
    window.gtag("js", new Date());
    if (site.google_analytics_id) window.gtag("config", site.google_analytics_id, { send_page_view: false });
    if (site.google_ads_id) window.gtag("config", site.google_ads_id, { send_page_view: false });
  }

  if (site.meta_pixel_id && !window.fbq) {
    window.fbq = function fbq(){ window.fbq.callMethod ? window.fbq.callMethod.apply(window.fbq, arguments) : window.fbq.queue.push(arguments); };
    window.fbq.push = window.fbq;
    window.fbq.loaded = true;
    window.fbq.version = "2.0";
    window.fbq.queue = [];
    addScript("meta-pixel-script", "https://connect.facebook.net/en_US/fbevents.js");
    window.fbq("init", site.meta_pixel_id);
  }
}

export function trackPageView(site, path, title = document.title) {
  if (!site) return;
  const page_location = window.location.href;
  const page_path = path || `${window.location.pathname}${window.location.search}`;

  if (window.dataLayer && site.google_tag_manager_id) {
    window.dataLayer.push({
      event: "page_view",
      page_location,
      page_path,
      page_title: title,
    });
  }

  if (window.gtag && site.google_analytics_id) {
    window.gtag("event", "page_view", {
      page_location,
      page_path,
      page_title: title,
      send_to: site.google_analytics_id,
    });
  }

  if (window.gtag && site.google_ads_id) {
    window.gtag("event", "page_view", {
      page_location,
      page_path,
      page_title: title,
      send_to: site.google_ads_id,
    });
  }

  if (window.fbq && site.meta_pixel_id) {
    window.fbq("track", "PageView");
  }
}

export function trackBookingConversion(site, booking) {
  const value = Number(booking?.total_dollars || booking?.total_cents / 100 || 0);
  const payload = {
    transaction_id: booking?.id,
    value,
    currency: "USD",
    tour_name: booking?.slot?.tour?.name || "Tour booking",
    party_size: booking?.party_size || 1,
  };

  if (window.dataLayer && site?.google_tag_manager_id) {
    window.dataLayer.push({
      event: "booking_purchase",
      ...payload,
    });
  }

  if (window.gtag && site?.google_ads_id && site?.google_ads_booking_conversion_label) {
    window.gtag("event", "conversion", {
      send_to: `${site.google_ads_id}/${site.google_ads_booking_conversion_label}`,
      value,
      currency: "USD",
      transaction_id: booking?.id,
    });
  }

  if (window.gtag && site?.google_analytics_id) {
    window.gtag("event", "purchase", {
      transaction_id: payload.transaction_id,
      value,
      currency: "USD",
      items: [{
        item_name: payload.tour_name,
        quantity: payload.party_size,
        price: booking?.price_per_person_cents ? booking.price_per_person_cents / 100 : undefined,
      }],
    });
  }

  if (window.fbq && site?.meta_pixel_id) {
    window.fbq("track", "Purchase", { value, currency: "USD" });
  }
}
