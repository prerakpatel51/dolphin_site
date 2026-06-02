"use client";

import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api } from "../lib/api.js";
import { useSite } from "../lib/site.js";
import { absoluteUrl, breadcrumbJsonLd, graphJsonLd, localBusinessJsonLd, originUrl } from "../lib/seo.js";
import Calendar from "../components/Calendar.jsx";
import SEO from "../components/SEO.jsx";

export default function TourDetail({ initialTour = null, initialDates = {} }) {
  const { slug } = useParams();
  const [tour, setTour] = useState(initialTour);
  const [dates, setDates] = useState(initialDates);
  const [selected, setSelected] = useState(null);
  const [selectedSlotId, setSelectedSlotId] = useState("");
  const [partySize, setPartySize] = useState(3);
  const [travelers, setTravelers] = useState([]);
  const [formError, setFormError] = useState("");
  const { site } = useSite("tours");
  const nav = useNavigate();
  const [loadState, setLoadState] = useState(initialTour ? "ready" : "loading");

  useEffect(() => {
    let alive = true;
    const hasInitialTour = initialTour?.slug === slug;
    if (hasInitialTour) {
      setTour(initialTour);
      setDates(initialDates);
      setLoadState("ready");
    } else {
      setTour(null);
      setDates({});
      setLoadState("loading");
    }
    Promise.allSettled([
      api.tour(slug),
      api.tourDates(slug),
    ]).then(([tourResult, datesResult]) => {
      if (!alive) return;
      if (tourResult.status === "fulfilled") {
        setTour(tourResult.value);
        setLoadState("ready");
      } else if (!hasInitialTour) {
        setTour(null);
        setLoadState("not-found");
      }
      if (datesResult.status === "fulfilled") setDates(datesResult.value.dates || {});
    });
    setSelected(null);
    setSelectedSlotId("");
    setFormError("");
    return () => { alive = false; };
  }, [slug, initialTour, initialDates]);

  if (loadState === "not-found") return (
    <div className="max-w-3xl mx-auto px-4 py-16 text-center">
      <SEO
        title="Tour Not Found | Dolphin Island Tours"
        description="This Dolphin Island Tours departure page could not be found. Browse current Merritt Island boat tours."
        canonical={`/tours/${slug}`}
      />
      <p className="uppercase tracking-[0.18em] text-ocean-500 text-xs mb-2">Tour not found</p>
      <h1 className="text-3xl sm:text-5xl mb-3">That tour is not available.</h1>
      <p className="text-ocean-700 mb-6">It may have been renamed, removed, or temporarily paused.</p>
      <Link className="btn-primary" to="/tours">Browse current tours</Link>
    </div>
  );
  if (!tour) return <div className="max-w-4xl mx-auto p-10">Loading…</div>;

  const slotsForDay = selected ? dates[selected] || [] : [];
  const selectedSlot = slotsForDay.find(s => String(s.id) === String(selectedSlotId));
  const minParty = tour.min_party || 3;
  const maxParty = Math.min(tour.max_party || 6, selectedSlot?.seats_remaining || tour.max_party || 6);
  const subtotal = partySize * tour.price_per_person;

  function updatePartySize(next) {
    const size = Math.min(Math.max(next, minParty), maxParty);
    setPartySize(size);
    setTravelers(current => {
      const copy = [...current];
      while (copy.length < size) copy.push({ name: "", age: "" });
      return copy.slice(0, size);
    });
  }

  function updateTraveler(index, key, value) {
    setTravelers(current => current.map((t, i) => i === index ? { ...t, [key]: value } : t));
  }

  function continueToPayment() {
    setFormError("");
    if (!selected || !selectedSlot) {
      setFormError("Choose a date and time.");
      return;
    }
    if (travelers.length !== partySize || travelers.some(t => !t.name.trim() || t.age === "")) {
      setFormError("Enter every traveler name and age.");
      return;
    }
    const cleanedTravelers = travelers.map(t => ({ name: t.name.trim(), age: Number(t.age) }));
    if (cleanedTravelers.some(t => Number.isNaN(t.age) || t.age < 0 || t.age > 120)) {
      setFormError("Traveler ages must be between 0 and 120.");
      return;
    }
    const pending = {
      slot_id: selectedSlot.id,
      tour_slug: slug,
      party_size: partySize,
      travelers: cleanedTravelers,
    };
    sessionStorage.setItem(`pendingBooking:${selectedSlot.id}`, JSON.stringify(pending));
    nav(`/book/${slug}?slot=${selectedSlot.id}`);
  }

  return (
    <div>
      <SEO
        title={tour.seo_title || `${tour.name} – Dolphin Island Tours`}
        description={tour.seo_description || tour.short_description}
        keywords={tour.seo_keywords}
        image={tour.og_image_url || tour.image_url}
        type="product"
        canonical={`/tours/${tour.slug}`}
        jsonLd={graphJsonLd([
          localBusinessJsonLd(site, tour.image_url),
          breadcrumbJsonLd([
            { name: "Home", path: "/" },
            { name: "Tours", path: "/tours" },
            { name: tour.name, path: `/tours/${tour.slug}` },
          ]),
          {
            "@type": ["TouristTrip", "Service"],
            "@id": `${originUrl()}/tours/${tour.slug}#tour`,
            "name": tour.name,
            "description": tour.long_description || tour.short_description,
            "image": absoluteUrl(tour.og_image_url || tour.image_url),
            "url": `${originUrl()}/tours/${tour.slug}`,
            "provider": { "@id": `${originUrl()}/#business` },
            "areaServed": ["Merritt Island", "Cocoa Beach", "Cape Canaveral", "Port Canaveral", "Kennedy Space Center", "Indian River Lagoon", "Florida Space Coast"],
            "offers": {
              "@type": "Offer",
              "price": String(tour.price_per_person),
              "priceCurrency": "USD",
              "availability": "https://schema.org/InStock",
              "url": `${originUrl()}/tours/${tour.slug}`,
            },
            "touristType": ["Families", "Couples", "Private groups", "Small groups", "Space Coast visitors"],
          },
        ])}
      />
      <section className="relative h-[52svh] min-h-[360px] sm:h-[55vh] overflow-hidden">
        <img src={tour.image_url || "/images/welcome.jpg"} alt={tour.name} fetchPriority="high" className="absolute inset-0 w-full h-full object-cover" />
        <div className="absolute inset-0 bg-gradient-to-t from-ocean-950/80 via-ocean-950/30 to-transparent" />
        <div className="relative max-w-5xl mx-auto px-4 h-full flex flex-col justify-end pb-8 sm:pb-10 text-white">
          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-display leading-[1.05]">{tour.name}</h1>
          <p className="mt-3 text-base sm:text-lg text-ocean-100 max-w-2xl">{tour.short_description}</p>
          <div className="mt-4 sm:mt-5 flex flex-wrap gap-2 text-xs sm:text-sm">
            <Badge>{tour.duration_minutes} minutes</Badge>
            <Badge>${tour.price_per_person} per person</Badge>
            <Badge>{tour.min_party}-{tour.max_party} guests</Badge>
          </div>
        </div>
      </section>

      <div className="max-w-6xl mx-auto px-4 py-8 sm:py-12">
        <section className="max-w-3xl mx-auto">
          <div className="card p-4 sm:p-7 h-fit">
            <p className="uppercase tracking-[0.18em] text-ocean-500 text-xs mb-2">Step 1</p>
            <h3 className="text-xl mb-1">Choose your departure</h3>
            <p className="text-sm text-ocean-600 mb-4">Pick a date, time, party size, and traveler names before payment.</p>
            <Calendar available={dates} selected={selected} onSelect={(day) => { setSelected(day); setSelectedSlotId(""); setFormError(""); }} />

            {selected && (
              <div className="mt-5 border-t border-ocean-100 pt-4">
                <div className="text-sm font-semibold text-ocean-900 mb-3">
                  {new Date(selected + "T00:00:00").toLocaleDateString(undefined,
                    { weekday: "long", month: "long", day: "numeric" })}
                </div>
                {slotsForDay.length === 0 && <p className="text-ocean-600 text-sm">No times available.</p>}
                <div className="grid grid-cols-2 gap-2">
                  {slotsForDay.map(s => {
                    const active = String(selectedSlotId) === String(s.id);
                    return (
                      <button
                        type="button"
                        key={s.id}
                        onClick={() => { setSelectedSlotId(String(s.id)); updatePartySize(Math.min(partySize, s.seats_remaining)); }}
                        className={`rounded-xl border px-3 py-2.5 text-left text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-ocean-400 ${active ? "border-ocean-600 bg-ocean-600 text-white shadow-lg shadow-ocean-600/20" : "border-ocean-200 bg-white text-ocean-800 hover:border-ocean-500"}`}
                      >
                        <span className="font-semibold">{s.time}</span>
                        <span className={`block text-xs ${active ? "text-ocean-100" : "text-ocean-500"}`}>{s.seats_remaining} seats left</span>
                      </button>
                    );
                  })}
                </div>
              </div>
            )}

            {selectedSlot && (
              <div className="mt-5 border-t border-ocean-100 pt-4 space-y-4">
                <div>
                  <label className="label">People traveling</label>
                  <div className="flex flex-wrap items-center gap-3">
                    <button type="button" className="btn-ghost !py-2 !px-4" onClick={() => updatePartySize(partySize - 1)}>−</button>
                    <span className="text-2xl font-display w-12 text-center">{partySize}</span>
                    <button type="button" className="btn-ghost !py-2 !px-4" onClick={() => updatePartySize(partySize + 1)}>+</button>
                    <span className="text-ocean-500 text-sm">{minParty}-{maxParty} guests</span>
                  </div>
                </div>

                <div className="space-y-3">
                  <div>
                    <h4 className="font-semibold text-ocean-900">Traveler details</h4>
                    <p className="text-xs text-ocean-600">Names and ages help us prepare safety gear and life jackets.</p>
                  </div>
                  {travelers.map((traveler, index) => (
                    <div key={index} className="rounded-xl border border-ocean-100 bg-ocean-50/50 p-3">
                      <div className="text-xs font-semibold uppercase tracking-wider text-ocean-500 mb-2">Guest {index + 1}</div>
                      <div className="grid grid-cols-[minmax(0,1fr)_5.5rem] gap-2">
                        <input
                          className="input !py-2"
                          placeholder="Full name"
                          value={traveler.name}
                          onChange={e => updateTraveler(index, "name", e.target.value)}
                        />
                        <input
                          className="input !py-2"
                          type="number"
                          min="0"
                          max="120"
                          placeholder="Age"
                          value={traveler.age}
                          onChange={e => updateTraveler(index, "age", e.target.value)}
                        />
                      </div>
                    </div>
                  ))}
                </div>

                <div className="rounded-xl bg-white border border-ocean-100 p-4">
                  <div className="flex justify-between text-sm text-ocean-700">
                    <span>{partySize} × ${tour.price_per_person}</span>
                    <span>${subtotal}</span>
                  </div>
                  <div className="flex justify-between text-sm text-ocean-700 mt-1">
                    <span>Taxes/fees</span>
                    <span>Calculated at payment</span>
                  </div>
                  <button type="button" onClick={continueToPayment} className="btn-primary w-full mt-4">
                    Continue to contact & payment
                  </button>
                  {formError && <p className="text-red-600 text-sm mt-3">{formError}</p>}
                </div>
              </div>
            )}
            {!selected && Object.keys(dates).length === 0 && (
              <p className="text-ocean-600 text-sm mt-4">No upcoming slots — check back soon.</p>
            )}
          </div>
        </section>

        <section className="max-w-3xl mx-auto mt-12 sm:mt-16">
          <h2 className="text-2xl mb-3">About this tour</h2>
          <p className="text-ocean-800 whitespace-pre-line">{tour.long_description}</p>

          <h2 className="text-2xl mt-10 mb-3">What to bring</h2>
          <ul className="list-disc pl-5 text-ocean-800 space-y-1">
            <li>Sunscreen, hat, sunglasses</li>
            <li>Water bottle</li>
            <li>Camera or phone</li>
            <li>Light layer (it's breezier on the water)</li>
          </ul>
        </section>
      </div>
    </div>
  );
}

function Badge({ children }) {
  return <span className="rounded-full bg-white/15 backdrop-blur text-white border border-white/25 px-3 py-1">{children}</span>;
}
