"use client";

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import SEO from "../components/SEO.jsx";
import { Stars, StarInput } from "../components/Stars.jsx";
import { api } from "../lib/api.js";
import { useAuth } from "../lib/auth.jsx";
import { imageFrom, useSite } from "../lib/site.js";
import { formatPhotoSize, MAX_REVIEW_PHOTOS, prepareReviewPhotos } from "../lib/reviewPhotos.js";

const REVIEW_TITLE_MAX = 80;
const REVIEW_BODY_MAX = 1000;

export default function ReviewsPage() {
  const { site } = useSite("home");
  const { user } = useAuth();
  const [tours, setTours] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [reviewableTours, setReviewableTours] = useState([]);
  const [stats, setStats] = useState({ count: 0, average: 0, breakdown: {} });
  const [tourFilter, setTourFilter] = useState("");
  const [selectedReviewTour, setSelectedReviewTour] = useState("");
  const [ratingFilter, setRatingFilter] = useState("");
  const [sort, setSort] = useState("helpful");
  const [visibleCount, setVisibleCount] = useState(9);
  const [form, setForm] = useState({ author_name: "", author_email: "", rating: 5, title: "", body: "" });
  const [photos, setPhotos] = useState([]);
  const [photoPreviews, setPhotoPreviews] = useState([]);
  const [photoBusy, setPhotoBusy] = useState(false);
  const [photoMessage, setPhotoMessage] = useState("");
  const [sent, setSent] = useState(false);
  const [pendingSubmission, setPendingSubmission] = useState(false);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const heroImage = imageFrom(site, "hero", "/images/hero-ocean.jpg");

  useEffect(() => {
    let alive = true;
    Promise.allSettled([api.tours(), api.allReviewStats()]).then(([tourResult, statsResult]) => {
      if (!alive) return;
      if (tourResult.status === "fulfilled") setTours(tourResult.value.results || tourResult.value);
      if (statsResult.status === "fulfilled") setStats(statsResult.value);
    });
    return () => { alive = false; };
  }, []);

  useEffect(() => {
    let alive = true;
    if (!user) {
      setReviewableTours([]);
      return () => { alive = false; };
    }
    api.myBookings().then(d => {
      if (!alive) return;
      const unique = new Map();
      (d.results || d)
        .filter(b => b.status === "paid" && b.slot?.tour?.slug)
        .forEach(b => unique.set(b.slot.tour.slug, b.slot.tour));
      const slugs = [...unique.keys()];
      setReviewableTours([...unique.values()]);
      setSelectedReviewTour(current => current || slugs[0] || "");
    }).catch(() => {
      if (alive) {
        setReviewableTours([]);
      }
    });
    return () => { alive = false; };
  }, [user]);

  useEffect(() => {
    if (!user) return;
    setForm(f => ({
      ...f,
      author_name: `${user.first_name || ""} ${user.last_name || ""}`.trim() || user.username,
      author_email: user.email || "",
    }));
  }, [user]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const requestedTour = params.get("tour");
    if (requestedTour) {
      setTourFilter(requestedTour);
      setSelectedReviewTour(requestedTour);
    }
  }, []);

  useEffect(() => {
    if (!user || selectedReviewTour || tours.length === 0) return;
    setSelectedReviewTour(tours[0].slug || "");
  }, [selectedReviewTour, tours, user]);

  useEffect(() => {
    let alive = true;
    const params = { sort };
    if (tourFilter) params.tour = tourFilter;
    if (ratingFilter) params.rating = ratingFilter;
    api.reviews(params).then(d => {
      if (!alive) return;
      setReviews(d.results || d);
      setVisibleCount(9);
    }).catch(() => {
      if (alive) setReviews([]);
    });
    return () => { alive = false; };
  }, [tourFilter, ratingFilter, sort]);

  useEffect(() => {
    const previews = photos.map(photo => ({
      name: photo.name,
      size: photo.size,
      url: URL.createObjectURL(photo),
    }));
    setPhotoPreviews(previews);
    return () => previews.forEach(preview => URL.revokeObjectURL(preview.url));
  }, [photos]);

  const tourOptions = tours;
  const breakdown = stats.breakdown || {};
  const visibleReviews = reviews.slice(0, visibleCount);
  const paidTourSlugs = new Set(reviewableTours.map(tour => tour.slug));
  const selectedIsVerified = paidTourSlugs.has(selectedReviewTour);

  async function submit(e) {
    e.preventDefault();
    if (photoBusy) {
      setErr("Photos are still being prepared. Try again in a moment.");
      return;
    }
    if (!selectedReviewTour) {
      setErr("Choose the tour you want to review.");
      return;
    }
    if (photos.length > MAX_REVIEW_PHOTOS) {
      setErr(`Upload up to ${MAX_REVIEW_PHOTOS} images.`);
      return;
    }
    setBusy(true);
    setErr("");
    try {
      const payload = new FormData();
      Object.entries({ ...form, tour_slug: selectedReviewTour }).forEach(([key, value]) => payload.append(key, value));
      photos.forEach(photo => payload.append("photos", photo));
      const res = await api.submitReview(payload);
      setSent(true);
      setPendingSubmission(Boolean(res?.pending_moderation));
      setPhotos([]);
      setForm(f => ({ ...f, title: "", body: "", rating: 5 }));
      if (res?.review && !res.pending_moderation && (!tourFilter || res.review.tour_slug === tourFilter)) {
        setReviews(items => [res.review, ...items.filter(review => review.id !== res.review.id)]);
      }
    } catch (e) {
      setErr(e.message);
    } finally {
      setBusy(false);
    }
  }

  async function handlePhotoChange(e) {
    setPhotoBusy(true);
    setErr("");
    setPhotoMessage("");
    try {
      const result = await prepareReviewPhotos(e.target.files);
      setPhotos(result.files);
      setPhotoMessage(result.warnings.join(" "));
    } catch (error) {
      setPhotos([]);
      setErr(error.message || "Photos could not be prepared.");
    } finally {
      setPhotoBusy(false);
      e.target.value = "";
    }
  }

  return (
    <div>
      <SEO
        title={`Guest Reviews | ${site.site_name}`}
        description="Read verified guest reviews for Dolphin Island Tours across wildlife, sunset, dolphin, and Space Coast boat tours."
        image={heroImage}
        canonical="/reviews"
      />

      <section className="bg-white border-b border-ocean-100">
        <div className="max-w-6xl mx-auto px-4 py-12 sm:py-16">
          <p className="uppercase tracking-[0.3em] text-ocean-500 text-xs mb-3">Guest reviews</p>
          <div className="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-6">
            <div>
              <h1 className="text-4xl sm:text-6xl font-display">Reviews from every tour.</h1>
              <p className="text-ocean-700 text-lg mt-4 max-w-2xl">
                Browse guest reviews across Dolphin Island Tours, then choose the trip that fits your day on the water.
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <Link to="/tours" className="btn-primary">Book a tour</Link>
              <a href="#write-review" className="btn-ghost">Write a review</a>
            </div>
          </div>
        </div>
      </section>

      <section className="max-w-6xl mx-auto px-4 py-10 sm:py-14">
        {stats.count > 0 && (
          <div className="grid lg:grid-cols-[260px_minmax(0,1fr)] gap-4 mb-8">
            <div className="card p-5 sm:p-6">
              <Stars value={stats.average} size={22} />
              <div className="mt-2 text-3xl font-display text-ocean-950">{Number(stats.average || 0).toFixed(1)} / 5</div>
              <div className="text-sm text-ocean-600">{stats.count} review{stats.count !== 1 ? "s" : ""}</div>
            </div>
            <div className="card p-5 sm:p-6">
              <div className="space-y-2">
                {[5, 4, 3, 2, 1].map(star => {
                  const count = Number(breakdown[String(star)] || 0);
                  const percent = stats.count ? Math.round((count / stats.count) * 100) : 0;
                  const active = ratingFilter === String(star);
                  return (
                    <button
                      key={star}
                      type="button"
                      onClick={() => setRatingFilter(active ? "" : String(star))}
                      className={`w-full grid grid-cols-[56px_minmax(0,1fr)_44px] items-center gap-3 text-left text-sm ${active ? "text-ocean-900 font-semibold" : "text-ocean-700"}`}
                      aria-pressed={active}
                    >
                      <span>{star} star</span>
                      <span className="h-3 rounded-full bg-ocean-100 overflow-hidden">
                        <span className="block h-full rounded-full bg-amber-400" style={{ width: `${percent}%` }} />
                      </span>
                      <span className="text-right tabular-nums">{percent}%</span>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        <div className="card p-4 sm:p-5 mb-8 flex flex-col lg:flex-row lg:items-end gap-4">
          <div className="flex-1">
            <label className="label" htmlFor="review-tour-filter">Tour</label>
            <select id="review-tour-filter" className="input" value={tourFilter} onChange={e => setTourFilter(e.target.value)}>
              <option value="">All tours</option>
              {tourOptions.map(tour => (
                <option key={tour.slug} value={tour.slug}>{tour.name}</option>
              ))}
            </select>
          </div>
          <div className="flex-1">
            <label className="label" htmlFor="review-rating-filter">Rating</label>
            <select id="review-rating-filter" className="input" value={ratingFilter} onChange={e => setRatingFilter(e.target.value)}>
              <option value="">All ratings</option>
              {[5, 4, 3, 2, 1].map(star => (
                <option key={star} value={star}>{star} star{star !== 1 ? "s" : ""}</option>
              ))}
            </select>
          </div>
          <div className="flex-1">
            <label className="label" htmlFor="review-sort">Sort</label>
            <select id="review-sort" className="input" value={sort} onChange={e => setSort(e.target.value)}>
              <option value="helpful">Most helpful</option>
              <option value="newest">Newest</option>
              <option value="highest">Highest rated</option>
              <option value="lowest">Lowest rated</option>
            </select>
          </div>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {visibleReviews.length === 0 && (
            <div className="card p-7 md:col-span-2 lg:col-span-3 text-center">
              <h2 className="text-xl">No reviews match those filters.</h2>
              <p className="text-ocean-700 mt-2">Try another tour or rating.</p>
            </div>
          )}
          {visibleReviews.map(review => (
            <ReviewArticle key={review.id} review={review} />
          ))}
        </div>

        {visibleCount < reviews.length && (
          <div className="mt-8 text-center">
            <button type="button" className="btn-ghost" onClick={() => setVisibleCount(c => c + 9)}>
              Load more reviews
            </button>
          </div>
        )}

        <section id="write-review" className="mt-20 scroll-mt-24">
          {!user ? (
            <div className="card p-8 sm:p-12 text-center bg-ocean-50 border-ocean-200">
              <h2 className="text-3xl font-display mb-4">Log in to write a review.</h2>
              <p className="text-ocean-700 text-lg max-w-2xl mx-auto mb-5">
                Reviews can only be written by logged-in guests. Reviews without a matching booking appear after admin approval.
              </p>
              <Link to="/login?next=/reviews#write-review" className="btn-primary">Log in to review</Link>
            </div>
          ) : tourOptions.length > 0 ? (
            <div className="card p-5 sm:p-8">
              <h2 className="text-3xl font-display mb-2">Leave a review</h2>
              <p className="text-ocean-700 text-sm mb-5">
                Logged-in guests can review any tour. Reviews tied to a paid booking publish with the Verified Guest tag; other reviews appear after admin approval.
              </p>
              {sent ? (
                <div className="mb-5 rounded-xl bg-emerald-50 border border-emerald-200 p-5 text-emerald-900">
                  <p className="font-semibold">Thanks for the review!</p>
                  <p className="text-sm mt-1">
                    {pendingSubmission
                      ? "It will appear publicly after admin approval."
                      : "It is live with the Verified Guest tag."}
                  </p>
                </div>
              ) : null}
              <form onSubmit={submit} className="space-y-4">
                <div>
                  <label className="label" htmlFor="review-tour">Tour *</label>
                  <select
                    id="review-tour"
                    className="input"
                    required
                    value={selectedReviewTour}
                    onChange={e => {
                      setSelectedReviewTour(e.target.value);
                      setSent(false);
                    }}
                  >
                    <option value="">Choose a tour</option>
                    {tourOptions.map(tour => (
                      <option key={tour.slug} value={tour.slug}>
                        {tour.name}{paidTourSlugs.has(tour.slug) ? " - verified booking" : ""}
                      </option>
                    ))}
                  </select>
                  {selectedReviewTour && selectedIsVerified && (
                    <p className="text-xs text-emerald-700 mt-1">This matches one of your paid bookings.</p>
                  )}
                  {selectedReviewTour && !selectedIsVerified && (
                    <p className="text-xs text-ocean-600 mt-1">This review will wait for admin approval before it appears publicly.</p>
                  )}
                </div>
                <div>
                  <label className="label" htmlFor="review-rating">Your rating</label>
                  <StarInput value={form.rating} onChange={v => setForm(f => ({ ...f, rating: v }))} />
                </div>
                <div className="grid sm:grid-cols-2 gap-3">
                  <div>
                    <label className="label" htmlFor="review-author-name">Your name *</label>
                    <input id="review-author-name" className="input" required value={form.author_name} onChange={e => setForm({ ...form, author_name: e.target.value })} />
                  </div>
                  <div>
                    <label className="label" htmlFor="review-author-email">Email (private)</label>
                    <input id="review-author-email" type="email" className="input" value={form.author_email} onChange={e => setForm({ ...form, author_email: e.target.value })} />
                  </div>
                </div>
                <div>
                  <label className="label" htmlFor="review-title">Title (optional)</label>
                  <input id="review-title" className="input" maxLength={REVIEW_TITLE_MAX} value={form.title} onChange={e => setForm({ ...form, title: e.target.value })} />
                  <div className="mt-1 text-right text-xs text-ocean-500">{form.title.length}/{REVIEW_TITLE_MAX}</div>
                </div>
                <div>
                  <label className="label" htmlFor="review-body">Your review *</label>
                  <textarea id="review-body" required maxLength={REVIEW_BODY_MAX} className="input min-h-[120px]" value={form.body} onChange={e => setForm({ ...form, body: e.target.value })} />
                  <div className="mt-1 flex items-center justify-between gap-3 text-xs text-ocean-500">
                    <span>Maximum {REVIEW_BODY_MAX} characters.</span>
                    <span className={form.body.length > REVIEW_BODY_MAX * 0.9 ? "text-amber-700 font-semibold" : ""}>{form.body.length}/{REVIEW_BODY_MAX}</span>
                  </div>
                </div>
                <div>
                  <label className="label" htmlFor="review-photos">Photos (optional, up to 5)</label>
                  <input
                    id="review-photos"
                    type="file"
                    accept="image/*"
                    multiple
                    className="input"
                    disabled={photoBusy}
                    onChange={handlePhotoChange}
                  />
                  <p className="mt-1 text-xs text-ocean-500">
                    {photoBusy ? "Preparing photos..." : "Large photos are resized before upload so five images can submit cleanly."}
                  </p>
                  {photoMessage && <p className="mt-1 text-xs text-amber-700">{photoMessage}</p>}
                  {photoPreviews.length > 0 && (
                    <div className="mt-3 grid grid-cols-2 sm:grid-cols-5 gap-3">
                      {photoPreviews.map((photo, index) => (
                        <div key={`${photo.name}-${index}`} className="rounded-lg border border-ocean-100 bg-ocean-50 overflow-hidden">
                          <img src={photo.url} alt="" className="aspect-square w-full object-cover" />
                          <div className="px-2 py-1.5 text-[11px] text-ocean-600">
                            <div className="truncate" title={photo.name}>{photo.name}</div>
                            <div>{formatPhotoSize(photo.size)}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
                {err && <p className="text-red-600 text-sm">{err}</p>}
                <button disabled={busy || photoBusy} className="btn-primary w-full sm:w-auto">
                  {busy ? "Sending..." : photoBusy ? "Preparing photos..." : "Submit review"}
                </button>
              </form>
            </div>
          ) : (
            <div className="card p-8 sm:p-12 text-center bg-ocean-50 border-ocean-200">
              <h2 className="text-3xl font-display mb-4">Reviews are opening soon.</h2>
              <p className="text-ocean-700 text-lg max-w-2xl mx-auto">Tours are still loading. Try again in a moment.</p>
            </div>
          )}
        </section>
      </section>
    </div>
  );
}

function ReviewArticle({ review }) {
  const photoUrls = review.photo_urls?.length ? review.photo_urls : (review.photo_url ? [review.photo_url] : []);
  return (
    <article className="card p-6">
      {photoUrls.length > 0 && (
        <div className={`mb-4 grid gap-2 ${photoUrls.length === 1 ? "" : "grid-cols-2"}`}>
          {photoUrls.map((url, index) => (
            <img
              key={url}
              src={url}
              alt=""
              className={`w-full object-cover rounded-lg ${photoUrls.length === 1 || index === 0 ? "aspect-[4/3]" : "aspect-square"}`}
              loading="lazy"
              decoding="async"
            />
          ))}
        </div>
      )}
      <div className="flex flex-wrap items-center gap-2">
        <Stars value={review.rating} />
        {review.tour_name && (
          <span className="text-[10px] uppercase tracking-wider rounded-full bg-ocean-100 text-ocean-800 px-2 py-0.5 font-semibold">
            {review.tour_name}
          </span>
        )}
        {review.verified_guest && (
          <span className="text-[10px] uppercase tracking-wider rounded-full bg-emerald-100 text-emerald-800 px-2 py-0.5 font-semibold">
            Verified Guest
          </span>
        )}
        {review.reviewer_type === "anonymous" && (
          <span className="text-[10px] uppercase tracking-wider rounded-full bg-ocean-100 text-ocean-700 px-2 py-0.5 font-semibold">
            Guest review
          </span>
        )}
      </div>
      {review.title && <h2 className="text-lg mt-3">{review.title}</h2>}
      <p className="text-ocean-800 mt-2 leading-relaxed whitespace-pre-line">"{review.body}"</p>
      {review.reply_text && (
        <div className="mt-4 rounded-lg border border-ocean-100 bg-ocean-50 p-4">
          <p className="text-xs uppercase tracking-[0.2em] text-ocean-500 font-semibold">Owner reply</p>
          <p className="text-ocean-800 mt-2 leading-relaxed whitespace-pre-line">{review.reply_text}</p>
        </div>
      )}
      <p className="text-sm text-ocean-500 mt-4">— {review.author_name} · {new Date(review.created_at).toLocaleDateString()}</p>
      {review.tour_slug && (
        <Link to={`/tours/${review.tour_slug}`} className="inline-flex mt-4 text-sm font-semibold text-ocean-700 hover:text-ocean-900 underline underline-offset-4">
          View this tour
        </Link>
      )}
    </article>
  );
}
