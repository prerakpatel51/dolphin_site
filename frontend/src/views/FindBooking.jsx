"use client";

import { useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api.js";
import { bookingDate, confirmationDataUrl, confirmationFilename } from "../lib/bookingReceipt.js";
import { useSite } from "../lib/site.js";
import SEO from "../components/SEO.jsx";

function money(cents = 0) {
  return `$${(Number(cents || 0) / 100).toFixed(2)}`;
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
  if (status === "payment_failed" || status === "cancelled" || status === "refunded") return "bg-red-100 text-red-800";
  if (status === "expired") return "bg-ocean-100 text-ocean-700";
  return "bg-amber-100 text-amber-800";
}

function canDownloadConfirmation(booking) {
  return booking.status === "paid";
}

export default function FindBooking() {
  const { site, page } = useSite("find_booking");
  const [form, setForm] = useState({ email: "", last_name: "" });
  const [results, setResults] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    setResults(null);
    try {
      const data = await api.lookupBookings({
        email: form.email.trim(),
        last_name: form.last_name.trim(),
      });
      setResults(data.results || []);
    } catch (err) {
      setError(err.message || "Booking lookup failed.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-10 sm:py-16">
      <SEO
        title={page.seo_title || "Find My Booking | Dolphin Island Tours"}
        description={page.seo_description || "Find your Dolphin Island Tours booking with your email and last name, then download your confirmation receipt."}
        keywords={page.seo_keywords}
        canonical="/find-booking"
        robots="noindex, follow"
      />
      <div className="max-w-2xl mb-8">
        <p className="uppercase tracking-[0.18em] text-ocean-500 text-xs mb-2">Booking lookup</p>
        <h1 className="text-3xl sm:text-4xl mb-3">Find your booking</h1>
        <p className="text-ocean-700">
          Use the email and last name from the booking contact to view confirmations and download receipts.
        </p>
      </div>

      <form onSubmit={submit} className="card p-5 sm:p-6 grid sm:grid-cols-[minmax(0,1fr)_220px_auto] gap-x-4 gap-y-1 items-end">
        <div>
          <label className="label" htmlFor="lookup-email">Email</label>
          <input
            id="lookup-email"
            className="input"
            type="email"
            value={form.email}
            onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
            required
          />
        </div>
        <div>
          <label className="label" htmlFor="lookup-last-name">Last name</label>
          <input
            id="lookup-last-name"
            className="input"
            value={form.last_name}
            onChange={e => setForm(f => ({ ...f, last_name: e.target.value }))}
            placeholder="e.g. Patel"
            required
          />
        </div>
        <button className="btn-primary disabled:opacity-50" disabled={busy}>
          {busy ? "Searching..." : "Find booking"}
        </button>
        <p className="text-xs text-ocean-500 sm:col-span-3 mt-1">The last name entered on the booking.</p>
      </form>

      {error && (
        <div className="mt-5 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-red-700">
          {error}
        </div>
      )}

      {results && (
        <div className="mt-8 space-y-4">
          <h2 className="text-2xl">Matching bookings</h2>
          {results.length === 0 ? (
            <div className="card p-6">
              <p className="text-ocean-700">
                No booking matched that email and last name. Check the exact booking contact details from your email confirmation.
              </p>
              <Link className="btn-ghost !py-2 !px-4 mt-4 inline-flex" to="/contact">Contact us</Link>
            </div>
          ) : results.map(booking => (
            <div key={booking.id} className="card p-5 sm:p-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2 mb-2">
                  <div className="font-semibold text-lg">{booking.slot.tour?.name || "Dolphin Island Tours"}</div>
                  <span className={`text-xs rounded-full px-2 py-1 ${statusClass(booking.status)}`}>{statusLabel(booking.status)}</span>
                </div>
                <div className="text-ocean-700 text-sm">
                  {bookingDate(booking)} at {booking.slot.time.slice(0, 5)} · {booking.party_size} guests
                </div>
                <div className="text-ocean-600 text-sm mt-1">
                  Booked by {booking.customer_name}
                </div>
                <div className="text-ocean-600 text-sm">
                  Confirmation #{booking.id}
                </div>
              </div>
              <div className="flex flex-col sm:flex-row md:flex-col items-stretch sm:items-center md:items-end gap-3">
                <div className="text-2xl font-display">{money(booking.total_cents)}</div>
                {canDownloadConfirmation(booking) ? (
                  <a
                    href={confirmationDataUrl(booking, site)}
                    download={confirmationFilename(booking)}
                    className="btn-ghost !py-2 !px-4 text-sm text-center"
                  >
                    Download receipt
                  </a>
                ) : (
                  <span className="inline-flex items-center justify-center rounded-full border border-ocean-100 bg-ocean-50 px-4 py-2 text-sm font-semibold text-ocean-500">
                    Receipt unavailable
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
