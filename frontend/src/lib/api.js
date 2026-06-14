const BASE = process.env.NEXT_PUBLIC_API_BASE || "/api";

function cookieValue(name) {
  return document.cookie
    .split("; ")
    .find((row) => row.startsWith(`${name}=`))
    ?.split("=")
    .slice(1)
    .join("=") || "";
}

function csrfHeaders(method = "POST") {
  if (["GET", "HEAD", "OPTIONS", "TRACE"].includes(method.toUpperCase())) return {};
  const token = decodeURIComponent(cookieValue("csrftoken"));
  return token ? { "X-CSRFToken": token } : {};
}

function errorMessage(err) {
  if (err.detail) return err.detail;
  if (typeof err === "string") return err;
  if (err && typeof err === "object") {
    return Object.entries(err)
      .map(([field, messages]) => {
        const text = Array.isArray(messages) ? messages.join(" ") : String(messages);
        return `${field.replaceAll("_", " ")}: ${text}`;
      })
      .join(" ");
  }
  return "Request failed";
}

async function request(path, { method = "GET", body } = {}) {
  const isFormData = typeof FormData !== "undefined" && body instanceof FormData;
  const headers = { ...(isFormData ? {} : { "Content-Type": "application/json" }), ...csrfHeaders(method) };
  const r = await fetch(`${BASE}${path}`, {
    method, headers,
    body: body ? (isFormData ? body : JSON.stringify(body)) : undefined,
    credentials: "include",
  });
  if (!r.ok) {
    const err = await r.json().catch(() => ({ detail: r.statusText }));
    throw new Error(errorMessage(err));
  }
  if (r.status === 204) return null;
  return r.json();
}

export const api = {
  config: () => request("/config/"),
  tours: () => request("/tours/"),
  tour: (slug) => request(`/tours/${slug}/`),
  slots: (tourSlug) => request(`/slots/${tourSlug ? `?tour=${tourSlug}` : ""}`),
  slot: (id) => request(`/slots/${id}/`),
  tourDates: (slug) => request(`/tours/${slug}/dates/`),
  site: () => request("/site/"),
  contact: (d) => request("/contact/", { method: "POST", body: d }),
  validatePromo: (d) => request("/promo/validate/", { method: "POST", body: d }),
  lookupBookings: (d) => request("/bookings/lookup/", { method: "POST", body: d }),
  createAndPay: (d) => request("/bookings/create-and-pay/", { method: "POST", body: d }),
};
