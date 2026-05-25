const BASE = import.meta.env.VITE_API_BASE || "/api";

export async function clearTokens() {
  await fetch(`${BASE}/auth/logout/`, { method: "POST", credentials: "include" }).catch(() => {});
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

async function refreshAuth() {
  const r = await fetch(`${BASE}/auth/refresh/`, { method: "POST", credentials: "include" });
  return r.ok;
}

async function request(path, { method = "GET", body, auth = true, optionalAuth = false, retry = true } = {}) {
  const headers = { "Content-Type": "application/json" };
  const r = await fetch(`${BASE}${path}`, {
    method, headers,
    body: body ? JSON.stringify(body) : undefined,
    credentials: "include",
  });
  if (r.status === 401 && auth && retry && await refreshAuth()) {
    return request(path, { method, body, auth, optionalAuth, retry: false });
  }
  if (r.status === 401 && optionalAuth) {
    return request(path, { method, body, auth: false, optionalAuth: false, retry: false });
  }
  if (!r.ok) {
    const err = await r.json().catch(() => ({ detail: r.statusText }));
    throw new Error(errorMessage(err));
  }
  if (r.status === 204) return null;
  return r.json();
}

export const api = {
  signup: (d) => request("/auth/signup/", { method: "POST", body: d, auth: false }),
  login: async (email, password) => {
    const r = await request("/auth/login/", { method: "POST", body: { email, password }, auth: false });
    return r;
  },
  me: () => request("/auth/me/"),
  updateMe: (d) => request("/auth/me/", { method: "PATCH", body: d }),
  deleteMe: () => request("/auth/me/", { method: "DELETE" }),
  config: () => request("/config/", { auth: false }),
  tours: () => request("/tours/", { auth: false }),
  tour: (slug) => request(`/tours/${slug}/`, { auth: false }),
  slots: (tourSlug) => request(`/slots/${tourSlug ? `?tour=${tourSlug}` : ""}`, { auth: false }),
  slot: (id) => request(`/slots/${id}/`, { auth: false }),
  tourDates: (slug) => request(`/tours/${slug}/dates/`, { auth: false }),
  site: () => request("/site/", { auth: false }),
  contact: (d) => request("/contact/", { method: "POST", body: d, auth: false }),
  passwordResetRequest: (email) => request("/auth/password-reset/", { method: "POST", body: { email }, auth: false }),
  passwordResetConfirm: (d) => request("/auth/password-reset-confirm/", { method: "POST", body: d, auth: false }),
  validatePromo: (d) => request("/promo/validate/", { method: "POST", body: d, auth: false }),
  reviews: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return request(`/reviews/${q ? `?${q}` : ""}`, { optionalAuth: true });
  },
  submitReview: (d) => request("/reviews/", { method: "POST", body: d }),
  reviewStats: (slug) => request(`/tours/${slug}/reviews/stats/`, { auth: false }),
  myBookings: () => request("/bookings/"),
  createAndPay: (d) => request("/bookings/create-and-pay/", { method: "POST", body: d }),
};
