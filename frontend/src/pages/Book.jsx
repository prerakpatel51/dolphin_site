import { useEffect, useRef, useState } from "react";
import { useNavigate, useParams, useSearchParams, Link } from "react-router-dom";
import { api } from "../lib/api.js";
import { useAuth } from "../lib/auth.jsx";
import { useSite } from "../lib/site.js";
import { trackBookingConversion } from "../lib/tracking.js";

export default function Book() {
  const { slug } = useParams();
  const [params] = useSearchParams();
  const slotId = params.get("slot");
  const { user } = useAuth();
  const { site } = useSite("tours");
  const nav = useNavigate();

  const [cfg, setCfg] = useState(null);
  const [slot, setSlot] = useState(null);
  const [pending, setPending] = useState(null);
  const [pendingMissing, setPendingMissing] = useState(false);
  const [form, setForm] = useState({
    customer_name: "",
    customer_email: "",
    customer_phone: "",
    special_requests: "",
  });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [cardReady, setCardReady] = useState(false);
  const cardRef = useRef(null);
  const cardEl = useRef(null);
  const [promoInput, setPromoInput] = useState("");
  const [promo, setPromo] = useState(null);
  const [promoErr, setPromoErr] = useState("");
  const [promoBusy, setPromoBusy] = useState(false);

  useEffect(() => {
    api.config().then(setCfg);
    api.slots(slug).then(d => {
      const list = d.results || d;
      const found = list.find(s => String(s.id) === String(slotId));
      setSlot(found);
      if (found) {
        const raw = sessionStorage.getItem(`pendingBooking:${found.id}`);
        if (raw) {
          try {
            const parsed = JSON.parse(raw);
            const travelers = Array.isArray(parsed.travelers) ? parsed.travelers : [];
            setPending({
              slot_id: found.id,
              tour_slug: slug,
              party_size: Number(parsed.party_size || travelers.length || found.tour?.min_party || 1),
              travelers,
            });
            setPendingMissing(false);
          } catch {
            setPending(null);
            setPendingMissing(true);
          }
        } else {
          setPending(null);
          setPendingMissing(true);
        }
      }
    });
    if (user) setForm(f => ({ ...f,
      customer_name: `${user.first_name || ""} ${user.last_name || ""}`.trim() || user.username,
      customer_email: user.email, customer_phone: user.phone || "" }));
  }, [slug, slotId, user]);

  useEffect(() => {
    if (!cfg || !slot || cfg.fake_payments) return;
    let disposed = false;
    async function init() {
      if (!cfg.square_app_id || !window.Square || !cardEl.current) return;
      setCardReady(false);
      cardRef.current = null;
      cardEl.current.innerHTML = "";
      const payments = window.Square.payments(cfg.square_app_id, cfg.square_location_id);
      const c = await payments.card();
      if (disposed) {
        c.destroy?.();
        return;
      }
      await c.attach(cardEl.current);
      if (disposed) {
        c.destroy?.();
        return;
      }
      cardRef.current = c;
      setCardReady(true);
    }
    init();
    return () => {
      disposed = true;
      setCardReady(false);
      cardRef.current?.destroy?.();
      cardRef.current = null;
      if (cardEl.current) cardEl.current.innerHTML = "";
    };
  }, [cfg, slot?.id]);

  if (!user) return (
    <div className="max-w-md mx-auto p-10 text-center">
      <p className="mb-4">Please log in to book.</p>
      <Link className="btn-primary" to={`/login?next=/book/${slug}?slot=${slotId}`}>Login</Link>
    </div>
  );
  if (!cfg || !slot) return <div className="p-10">Loading…</div>;

  const tour = slot.tour || {};
  const price = tour.price_per_person || cfg.price_per_person;
  const partySize = pending?.party_size || 0;
  const travelers = pending?.travelers || [];
  const subtotal = price * partySize;
  const discount = promo?.valid ? Math.round((promo.discount_cents || 0) / 100) : 0;
  const taxableTotal = Math.max(0, subtotal - discount);
  const taxRate = Number(cfg.tax_rate_percent || 0);
  const estimatedTax = Math.round(taxableTotal * taxRate) / 100;
  const total = taxableTotal + estimatedTax;
  const canSubmit = !pendingMissing && partySize > 0 && travelers.length === partySize
    && partySize <= slot.seats_remaining && form.customer_name && form.customer_email
    && /^\d{10}$/.test(form.customer_phone);

  async function applyPromo() {
    setPromoBusy(true); setPromoErr("");
    try {
      const r = await api.validatePromo({
        code: promoInput.trim(),
        email: form.customer_email,
        subtotal_cents: subtotal * 100,
      });
      if (!r.valid) { setPromo(null); setPromoErr(r.reason || "Invalid code."); }
      else setPromo(r);
    } catch (e) { setPromoErr(e.message); }
    finally { setPromoBusy(false); }
  }

  function clearPromo() {
    setPromo(null); setPromoInput(""); setPromoErr("");
  }

  async function submit(e) {
    e.preventDefault();
    setBusy(true); setError("");
    try {
      let source_id = null;
      if (!cfg.fake_payments) {
        if (!cardRef.current) throw new Error("Payment form still loading.");
        const tok = await cardRef.current.tokenize();
        if (tok.status !== "OK") throw new Error(tok.errors?.[0]?.message || "Card error");
        source_id = tok.token;
      }
      const booking = await api.createAndPay({
        slot_id: slot.id,
        party_size: partySize,
        travelers,
        ...form,
        source_id,
        promo_code: promo?.valid ? promo.code : "",
      });
      sessionStorage.removeItem(`pendingBooking:${slot.id}`);
      trackBookingConversion(site, booking);
      nav(`/bookings?just=${booking.id}`);
    } catch (e) { setError(e.message); }
    finally { setBusy(false); }
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 sm:py-12">
      <div className="mb-6 sm:mb-8">
        <p className="uppercase tracking-[0.18em] text-ocean-500 text-xs mb-2">Step 2</p>
        <h1 className="text-3xl sm:text-4xl mb-2">Contact & payment</h1>
        <p className="text-ocean-700 text-sm sm:text-base">
        {slot.tour?.name} · {new Date(slot.date + "T00:00:00").toLocaleDateString(undefined,
          { weekday: "long", month: "long", day: "numeric" })} at {slot.time.slice(0,5)}
        </p>
      </div>

      {pendingMissing && (
        <div className="rounded-2xl border border-amber-300 bg-amber-50 p-4 sm:p-5 mb-6 text-amber-950">
          <div className="font-semibold">Traveler details are missing.</div>
          <p className="text-sm mt-1">Choose the date, time, party size, and each traveler name before payment.</p>
          <Link className="btn-ghost !py-2 !px-4 mt-3 inline-flex" to={`/tours/${slug}`}>Return to tour page</Link>
        </div>
      )}

      <form onSubmit={submit} className="grid lg:grid-cols-[minmax(0,1fr)_360px] gap-5 sm:gap-6 items-start">
        <div className="card p-5 sm:p-8 space-y-5">
          <div>
            <h2 className="text-2xl mb-1">Booking contact</h2>
            <p className="text-sm text-ocean-600">This is the person who receives the receipt and trip updates.</p>
          </div>

          <div className="grid sm:grid-cols-2 gap-4">
            <Field label="Full name" value={form.customer_name} onChange={v => setForm(f => ({ ...f, customer_name: v }))} required />
            <Field label="Email" type="email" value={form.customer_email} onChange={v => setForm(f => ({ ...f, customer_email: v }))} required />
            <Field
              label="Phone"
              value={form.customer_phone}
              onChange={v => setForm(f => ({ ...f, customer_phone: v.replace(/\D/g, "").slice(0, 10) }))}
              required
              inputMode="numeric"
              pattern="\d{10}"
              maxLength={10}
              helper="Numbers only, exactly 10 digits."
            />
          </div>
          <div>
            <label className="label">Special requests (optional)</label>
            <textarea className="input min-h-[96px]" value={form.special_requests}
              onChange={e => setForm(f => ({ ...f, special_requests: e.target.value }))} />
          </div>

          {cfg.fake_payments ? (
            <div className="rounded-xl bg-amber-50 border border-amber-300 p-4 text-amber-900">
              <div className="font-semibold">Test mode - fake payment</div>
              <p className="text-sm mt-1">No card is charged. Click "Pretend to pay" to confirm the booking. Swap to Square at launch.</p>
            </div>
          ) : (
            <div className="border-t border-ocean-100 pt-5">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-3">
                <div>
                  <label className="label !mb-0">Payment card</label>
                  <p className="text-xs text-ocean-500 mt-1">Use a Square sandbox test card while this site is in test mode.</p>
                </div>
                <span className="inline-flex w-fit items-center gap-2 rounded-full bg-ocean-50 border border-ocean-100 px-3 py-1 text-xs font-semibold text-ocean-700">
                  Secured by Square
                </span>
              </div>
              <div className="rounded-2xl border border-ocean-200 bg-gradient-to-br from-white to-ocean-50/60 p-3 sm:p-4 shadow-inner shadow-ocean-900/5">
                <div
                  ref={cardEl}
                  className="square-card-host min-h-[58px] rounded-xl border border-ocean-200 bg-white p-2 sm:p-3"
                />
                {!cardReady && (
                  <div className="mt-3 rounded-lg bg-ocean-50 px-3 py-2 text-sm text-ocean-700">
                    Loading secure card field…
                  </div>
                )}
              </div>
              <p className="text-xs text-ocean-500 mt-2">Card details are encrypted by Square and never touch our server.</p>
            </div>
          )}

          <div className="border-t border-ocean-100 pt-5">
            <label className="label">Promo code (optional)</label>
            {promo?.valid ? (
              <div className="flex items-center justify-between gap-3 rounded-xl border border-emerald-300 bg-emerald-50 px-4 py-3">
                <div>
                  <div className="font-mono font-bold text-emerald-900">{promo.code}</div>
                  <div className="text-xs text-emerald-700">
                    {promo.kind === "percent" ? `${promo.percent_off}% off` : `$${(promo.amount_off_cents/100).toFixed(2)} off`}
                    {" "}— saved ${discount}
                  </div>
                </div>
                <button type="button" onClick={clearPromo} className="text-emerald-800 underline text-sm">Remove</button>
              </div>
            ) : (
              <div className="flex flex-col sm:flex-row gap-2">
                <input className="input flex-1 uppercase tracking-wider min-w-0" value={promoInput}
                  onChange={e => setPromoInput(e.target.value.toUpperCase())}
                  placeholder="E.g. DI1-AB23CD" />
                <button type="button" disabled={!promoInput || promoBusy}
                  onClick={applyPromo}
                  className="btn-ghost disabled:opacity-50">{promoBusy ? "…" : "Apply"}</button>
              </div>
            )}
            {promoErr && <p className="text-red-600 text-sm mt-2">{promoErr}</p>}
          </div>

          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-t border-ocean-100 pt-5">
            <div>
              <div className="text-ocean-600 text-sm">{partySize || 0} × ${price}{discount > 0 && ` − $${discount} off`}</div>
              <div className="text-3xl font-display">${total.toFixed(2)}</div>
            </div>
            <button disabled={!canSubmit || busy || (!cfg.fake_payments && !cardReady)} className="btn-primary disabled:opacity-50 w-full sm:w-auto">
              {busy ? "Processing…" : cfg.fake_payments ? `Pretend to pay $${total.toFixed(2)}` : `Pay $${total.toFixed(2)}`}
            </button>
          </div>
          {error && <p className="text-red-600">{error}</p>}
        </div>

        <aside className="card p-5 sm:p-6 lg:sticky lg:top-24">
          <h2 className="text-2xl mb-4">Trip summary</h2>
          <div className="space-y-3 text-sm">
            <SummaryRow label="Tour" value={slot.tour?.name} />
            <SummaryRow label="Date" value={new Date(slot.date + "T00:00:00").toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric", year: "numeric" })} />
            <SummaryRow label="Time" value={slot.time.slice(0,5)} />
            <SummaryRow label="Guests" value={partySize ? String(partySize) : "Not selected"} />
          </div>

          <div className="border-t border-ocean-100 mt-5 pt-5">
            <div className="font-semibold mb-3">Travelers</div>
            {travelers.length > 0 ? (
              <div className="space-y-2">
                {travelers.map((traveler, index) => (
                  <div key={`${traveler.name}-${index}`} className="rounded-xl bg-ocean-50 border border-ocean-100 px-3 py-2">
                    <div className="font-medium text-ocean-900">{traveler.name}</div>
                    <div className="text-xs text-ocean-600">Age {traveler.age}</div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-ocean-600">Traveler details were not found.</p>
            )}
          </div>

          <div className="border-t border-ocean-100 mt-5 pt-5 space-y-2 text-sm">
            <SummaryRow label={`${partySize || 0} × $${price}`} value={`$${subtotal}`} />
            {discount > 0 && <SummaryRow label="Promo discount" value={`-$${discount}`} />}
            <SummaryRow label={`Tax${taxRate > 0 ? ` (${taxRate.toFixed(2)}%)` : ""}`} value={`$${estimatedTax.toFixed(2)}`} />
            <div className="flex items-center justify-between pt-3 border-t border-ocean-100">
              <span className="font-semibold">Total due</span>
              <span className="text-3xl font-display">${total.toFixed(2)}</span>
            </div>
          </div>
        </aside>
      </form>
    </div>
  );
}

function Field({ label, value, onChange, type = "text", required, helper, inputMode, pattern, maxLength }) {
  return (
    <div>
      <label className="label">{label}{required && " *"}</label>
      <input
        className="input"
        type={type}
        value={value}
        required={required}
        inputMode={inputMode}
        pattern={pattern}
        maxLength={maxLength}
        onChange={e => onChange(e.target.value)}
      />
      {helper && <p className="text-xs text-ocean-500 mt-1">{helper}</p>}
    </div>
  );
}

function SummaryRow({ label, value }) {
  return (
    <div className="flex items-start justify-between gap-4">
      <span className="text-ocean-600">{label}</span>
      <span className="font-medium text-right text-ocean-950">{value}</span>
    </div>
  );
}
