"use client";

import { useEffect, useState } from "react";
import { useLocation, useSearchParams, Link, Navigate } from "react-router-dom";
import { api } from "../lib/api.js";
import { useAuth } from "../lib/auth.jsx";
import SEO from "../components/SEO.jsx";

function money(cents = 0) {
  return `$${(Number(cents || 0) / 100).toFixed(2)}`;
}

function escapeHtml(value = "") {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function bookingDate(booking) {
  return new Date(booking.slot.date + "T00:00:00").toLocaleDateString(undefined, {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

function confirmationFilename(booking) {
  return `dolphin-island-confirmation-${booking.id}.html`;
}

function confirmationHtml(booking) {
  const tourName = booking.slot.tour?.name || "Dolphin Island Tours";
  const travelerRows = (booking.travelers || []).map((traveler, index) => (
    `<li>${escapeHtml(traveler.name || `Guest ${index + 1}`)}${traveler.age !== undefined && traveler.age !== "" ? `, age ${escapeHtml(traveler.age)}` : ""}</li>`
  )).join("");
  return `<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Dolphin Island Tours Confirmation ${escapeHtml(booking.id)}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font-family: Arial, sans-serif; color: #0b3a52; margin: 0; padding: 32px; background: #f4fbfe; }
    .receipt { max-width: 720px; margin: 0 auto; background: white; border: 1px solid #d4edf5; border-radius: 14px; padding: 28px; }
    h1 { margin: 0 0 6px; color: #0b6a8a; }
    .muted { color: #557287; }
    .status { display: inline-block; padding: 5px 10px; border-radius: 999px; background: #dcfce7; color: #166534; font-size: 12px; font-weight: 700; text-transform: uppercase; }
    table { width: 100%; border-collapse: collapse; margin-top: 24px; }
    td { padding: 10px 0; border-bottom: 1px solid #e6f4f8; vertical-align: top; }
    td:first-child { font-weight: 700; width: 38%; }
    .total { font-size: 24px; font-weight: 800; color: #08384d; }
    .travelers { margin-top: 24px; padding: 18px; background: #f4fbfe; border: 1px solid #d4edf5; border-radius: 12px; }
    .travelers h2 { margin: 0 0 10px; font-size: 18px; }
    .travelers ol { margin: 0; padding-left: 22px; }
    .travelers li { margin: 5px 0; }
    .footer { margin-top: 24px; font-size: 13px; color: #557287; line-height: 1.5; }
    @media print { body { background: white; padding: 0; } .receipt { border: 0; } }
  </style>
</head>
<body>
  <main class="receipt">
    <h1>Dolphin Island Tours</h1>
    <p class="muted">Booking confirmation and receipt</p>
    <p><span class="status">${escapeHtml(booking.status)}</span></p>
    <table>
      <tr><td>Confirmation #</td><td>${escapeHtml(booking.id)}</td></tr>
      <tr><td>Tour</td><td>${escapeHtml(tourName)}</td></tr>
      <tr><td>Date</td><td>${escapeHtml(bookingDate(booking))}</td></tr>
      <tr><td>Time</td><td>${escapeHtml(booking.slot.time.slice(0, 5))}</td></tr>
      <tr><td>Guests</td><td>${escapeHtml(booking.party_size)}</td></tr>
      <tr><td>Name</td><td>${escapeHtml(booking.customer_name)}</td></tr>
      <tr><td>Email</td><td>${escapeHtml(booking.customer_email)}</td></tr>
      <tr><td>Phone</td><td>${escapeHtml(booking.customer_phone || "N/A")}</td></tr>
      <tr><td>Price per person</td><td>${money(booking.price_per_person_cents)}</td></tr>
      ${booking.discount_cents ? `<tr><td>Discount</td><td>-${money(booking.discount_cents)}${booking.promo_code_label ? ` (${escapeHtml(booking.promo_code_label)})` : ""}</td></tr>` : ""}
      <tr><td>Tax</td><td>${money(booking.tax_cents)}</td></tr>
      <tr><td>Total paid</td><td class="total">${money(booking.total_cents)}</td></tr>
      ${booking.special_requests ? `<tr><td>Special requests</td><td>${escapeHtml(booking.special_requests)}</td></tr>` : ""}
    </table>
    ${travelerRows ? `<section class="travelers"><h2>Travelers</h2><ol>${travelerRows}</ol></section>` : ""}
    <div class="footer">
      <p><b>Meeting point:</b> 2700 Harbortown Drive, Merritt Island, FL</p>
      <p>Please arrive 15 minutes before departure. Bring sunscreen, water, sunglasses, and a camera.</p>
      <p>Generated on ${escapeHtml(new Date().toLocaleString())}</p>
    </div>
  </main>
</body>
</html>`;
}

function confirmationDataUrl(booking) {
  return `data:text/html;charset=utf-8,${encodeURIComponent(confirmationHtml(booking))}`;
}

function canDownloadConfirmation(booking) {
  return booking.status === "paid";
}

function statusLabel(status) {
  return {
    paid: "paid",
    pending: "pending payment",
    payment_failed: "payment failed",
    expired: "expired hold",
    cancelled: "cancelled",
    refunded: "refunded",
  }[status] || status;
}

function statusClass(status) {
  if (status === "paid") return "bg-emerald-100 text-emerald-800";
  if (status === "payment_failed") return "bg-red-100 text-red-800";
  if (status === "expired") return "bg-ocean-100 text-ocean-700";
  if (status === "cancelled" || status === "refunded") return "bg-red-100 text-red-800";
  return "bg-amber-100 text-amber-800";
}

export default function MyBookings() {
  const { user, loading } = useAuth();
  const location = useLocation();
  const [list, setList] = useState([]);
  const [params] = useSearchParams();
  const justId = params.get("just");
  useEffect(() => { if (user) api.myBookings().then(d => setList(d.results || d)); }, [user]);

  if (loading) return <div className="p-10">Loading...</div>;
  if (!user) return <Navigate to={`/login?next=${encodeURIComponent(`${location.pathname}${location.search}`)}`} replace />;
  return (
    <div className="max-w-3xl mx-auto px-4 py-10 sm:py-16">
      <SEO
        title="My Bookings | Dolphin Island Tours"
        description="View your Dolphin Island Tours booking confirmations, receipts, traveler details, and trip status."
        canonical="/bookings"
        robots="noindex, follow"
      />
      <h1 className="text-3xl sm:text-4xl mb-6">My bookings</h1>
      {justId && (
        <div className="card p-6 mb-6 bg-emerald-50 border-emerald-200">
          <h3 className="text-xl">Booking confirmed!</h3>
          <p className="text-ocean-700">Receipt sent to your email.</p>
        </div>
      )}
      <div className="space-y-4">
        {list.map(b => (
          <div key={b.id} className="card p-5 sm:p-6 flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3">
            <div className="min-w-0">
              <div className="font-semibold text-lg">{b.slot.tour?.name}</div>
              <div className="text-ocean-700 text-sm">
                {new Date(b.slot.date + "T00:00:00").toLocaleDateString(undefined,
                  { weekday: "short", month: "short", day: "numeric" })} at {b.slot.time.slice(0,5)} · {b.party_size} guests
              </div>
              {b.travelers?.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-2">
                  {b.travelers.map((traveler, index) => (
                    <span key={`${b.id}-${index}`} className="rounded-full bg-ocean-50 border border-ocean-100 px-3 py-1 text-xs text-ocean-700">
                      {traveler.name} · {traveler.age}
                    </span>
                  ))}
                </div>
              )}
            </div>
            <div className="flex sm:flex-col items-stretch sm:items-end justify-between gap-3">
              <div className="flex items-center sm:flex-col sm:items-end justify-between gap-3">
                <div className="text-2xl font-display">{money(b.total_cents)}</div>
                <span className={`text-xs rounded-full px-2 py-1 ${statusClass(b.status)}`}>{statusLabel(b.status)}</span>
              </div>
              {b.status === "payment_failed" && (
                <p className="max-w-[16rem] text-right text-xs text-red-700">
                  No charge was made and this booking was not confirmed.
                </p>
              )}
              {b.status === "expired" && (
                <p className="max-w-[16rem] text-right text-xs text-ocean-600">
                  This unpaid hold expired and the seats were released.
                </p>
              )}
              {canDownloadConfirmation(b) ? (
                <a
                  href={confirmationDataUrl(b)}
                  download={confirmationFilename(b)}
                  aria-label={`Download confirmation for ${b.slot.tour?.name || "booking"} on ${bookingDate(b)}`}
                  className="btn-ghost !py-2 !px-4 text-sm"
                >
                  Download confirmation
                </a>
              ) : (
                <span className="inline-flex items-center justify-center rounded-full border border-ocean-100 bg-ocean-50 px-4 py-2 text-sm font-semibold text-ocean-500">
                  Confirmation unavailable
                </span>
              )}
            </div>
          </div>
        ))}
        {list.length === 0 && <p className="text-ocean-600">No bookings yet. <Link to="/tours" className="underline">Browse tours →</Link></p>}
      </div>
    </div>
  );
}
