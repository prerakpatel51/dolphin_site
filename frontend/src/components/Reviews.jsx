import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api.js";
import { useAuth } from "../lib/auth.jsx";
import { Stars, StarInput } from "./Stars.jsx";

const REVIEW_TITLE_MAX = 80;
const REVIEW_BODY_MAX = 1000;

export default function Reviews({ tourSlug }) {
  const { user } = useAuth();
  const [reviews, setReviews] = useState([]);
  const [ownReview, setOwnReview] = useState(null);
  const [stats, setStats] = useState({ count: 0, average: 0, breakdown: {} });
  const [form, setForm] = useState({ author_name: "", author_email: "", rating: 5, title: "", body: "" });
  const [photos, setPhotos] = useState([]);
  const [sort, setSort] = useState("newest");
  const [ratingFilter, setRatingFilter] = useState("");
  const [visibleCount, setVisibleCount] = useState(6);
  const [hasPaidBooking, setHasPaidBooking] = useState(false);
  const [checkingBooking, setCheckingBooking] = useState(false);
  const [sent, setSent] = useState(false);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  useEffect(() => {
    const params = { tour: tourSlug, sort };
    if (ratingFilter) params.rating = ratingFilter;
    api.reviews(params).then(d => {
      setReviews(d.results || d);
      setVisibleCount(6);
    });
    if (tourSlug) api.reviewStats(tourSlug).then(setStats);
    if (user) setForm(f => ({
      ...f,
      author_name: `${user.first_name || ""} ${user.last_name || ""}`.trim() || user.username,
      author_email: user.email,
    }));
  }, [tourSlug, user, sort, ratingFilter]);

  useEffect(() => {
    let alive = true;
    setOwnReview(null);
    if (!user || !tourSlug) return () => { alive = false; };
    api.reviews({ tour: tourSlug }).then(d => {
      if (!alive) return;
      const rows = d.results || d;
      setOwnReview(rows.find(r => r.mine) || null);
    }).catch(() => {
      if (alive) setOwnReview(null);
    });
    return () => { alive = false; };
  }, [tourSlug, user]);

  useEffect(() => {
    let alive = true;
    setHasPaidBooking(false);
    if (!user || !tourSlug) return () => { alive = false; };
    setCheckingBooking(true);
    api.myBookings()
      .then(d => {
        if (!alive) return;
        const bookings = d.results || d;
        setHasPaidBooking(bookings.some(b => b.status === "paid" && b.slot?.tour?.slug === tourSlug));
      })
      .catch(() => {
        if (alive) setHasPaidBooking(false);
      })
      .finally(() => {
        if (alive) setCheckingBooking(false);
      });
    return () => { alive = false; };
  }, [tourSlug, user]);

  const myReview = user ? (ownReview || reviews.find(r => r.mine)) : null;
  const visibleReviews = useMemo(() => reviews.slice(0, visibleCount), [reviews, visibleCount]);
  const hasMoreReviews = visibleCount < reviews.length;
  const breakdown = stats.breakdown || {};

  async function submit(e) {
    e.preventDefault();
    setBusy(true); setErr("");
    try {
      if (photos.length > 5) {
        setErr("Upload up to 5 images.");
        setBusy(false);
        return;
      }
      const payload = new FormData();
      Object.entries({ ...form, tour_slug: tourSlug }).forEach(([key, value]) => payload.append(key, value));
      photos.forEach(photo => payload.append("photos", photo));
      const res = await api.submitReview(payload);
      setSent(true);
      setPhotos([]);
      if (res?.review) {
        setOwnReview(res.review);
        setReviews(r => [res.review, ...r.filter(x => x.id !== res.review.id)]);
      }
    } catch (e) { setErr(e.message); }
    finally { setBusy(false); }
  }

  async function markHelpful(reviewId) {
    setReviews(items => items.map(r => (
      r.id === reviewId ? { ...r, helpful_by_me: true, helpful_count: (r.helpful_count || 0) + (r.helpful_by_me ? 0 : 1) } : r
    )));
    try {
      const res = await api.markReviewHelpful(reviewId);
      setReviews(items => items.map(r => (
        r.id === reviewId ? { ...r, helpful_by_me: res.helpful_by_me, helpful_count: res.helpful_count } : r
      )));
    } catch {
      setReviews(items => items.map(r => (
        r.id === reviewId ? { ...r, helpful_by_me: false, helpful_count: Math.max(0, (r.helpful_count || 1) - 1) } : r
      )));
    }
  }

  return (
    <section id="reviews" className="mt-12 sm:mt-16 scroll-mt-24">
      <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4 mb-6 sm:mb-8">
        <div>
          <p className="uppercase tracking-[0.3em] text-ocean-500 text-xs mb-2">Guest reviews</p>
          <h2 className="text-3xl sm:text-4xl">What guests say</h2>
        </div>
        {stats.count > 0 && (
          <div className="flex items-center gap-3">
            <Stars value={stats.average} size={22} />
            <div>
              <div className="text-xl font-display">{stats.average.toFixed(1)} / 5</div>
              <div className="text-sm text-ocean-600">{stats.count} review{stats.count !== 1 ? "s" : ""}</div>
            </div>
          </div>
        )}
      </div>

      {stats.count > 0 && (
        <div className="grid lg:grid-cols-[minmax(0,1fr)_260px] gap-5 mb-8">
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
            {ratingFilter && (
              <button type="button" onClick={() => setRatingFilter("")} className="mt-4 text-sm text-ocean-700 underline">
                Show all ratings
              </button>
            )}
          </div>
          <div className="card p-5 sm:p-6">
            <label className="label" htmlFor="review-sort">Sort reviews</label>
            <select id="review-sort" className="input" value={sort} onChange={e => setSort(e.target.value)}>
              <option value="newest">Newest</option>
              <option value="highest">Highest Rated</option>
              <option value="lowest">Lowest Rated</option>
              <option value="helpful">Most Helpful</option>
            </select>
            <p className="text-sm text-ocean-600 mt-3">
              Showing {reviews.length} review{reviews.length !== 1 ? "s" : ""}{ratingFilter ? ` with ${ratingFilter} star${ratingFilter !== "1" ? "s" : ""}` : ""}.
            </p>
          </div>
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-4 sm:gap-6 mb-6">
        {reviews.length === 0 && <p className="text-ocean-600 col-span-full">No reviews yet — be the first!</p>}
        {visibleReviews.map(r => (
          <article key={r.id} className={`card p-5 sm:p-6 ${r.pending ? "border-amber-300 bg-amber-50/40" : ""}`}>
            <div className="flex items-start justify-between gap-3">
              <Stars value={r.rating} />
              <div className="flex flex-wrap justify-end gap-2">
                {r.verified_guest && (
                  <span className="text-[10px] uppercase tracking-wider rounded-full bg-emerald-100 text-emerald-800 px-2 py-0.5 font-semibold">Verified Guest</span>
                )}
                {r.mine && (
                  <span className="text-[10px] uppercase tracking-wider rounded-full bg-ocean-100 text-ocean-800 px-2 py-0.5 font-semibold">Your review</span>
                )}
                {r.pending && (
                  <span className="text-[10px] uppercase tracking-wider rounded-full bg-amber-200 text-amber-900 px-2 py-0.5 font-semibold">Pending</span>
                )}
              </div>
            </div>
            {(r.photo_urls?.length || r.photo_url) && (
              <div className={`mt-4 grid gap-2 ${((r.photo_urls?.length || 0) > 1) ? "grid-cols-2" : ""}`}>
                {(r.photo_urls?.length ? r.photo_urls : [r.photo_url]).map((url, index) => (
                  <img
                    key={url}
                    src={url}
                    alt=""
                    className={`w-full object-cover rounded-lg ${index === 0 ? "aspect-[4/3]" : "aspect-square"}`}
                    loading="lazy"
                  />
                ))}
              </div>
            )}
            {r.title && <h3 className="text-lg mt-2">{r.title}</h3>}
            <p className="text-ocean-800 mt-2 leading-relaxed whitespace-pre-line">{r.body}</p>
            {r.reply_text && (
              <div className="mt-4 rounded-lg border border-ocean-100 bg-ocean-50 p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-ocean-500 font-semibold">Owner reply</p>
                <p className="text-ocean-800 mt-2 leading-relaxed whitespace-pre-line">{r.reply_text}</p>
              </div>
            )}
            <p className="text-sm text-ocean-500 mt-4">— {r.author_name} · {new Date(r.created_at).toLocaleDateString()}</p>
            <button
              type="button"
              disabled={r.helpful_by_me}
              onClick={() => markHelpful(r.id)}
              className={`mt-4 text-sm font-semibold ${r.helpful_by_me ? "text-ocean-500" : "text-ocean-700 hover:text-ocean-900"}`}
            >
              Helpful{r.helpful_count ? ` (${r.helpful_count})` : ""}
            </button>
          </article>
        ))}
      </div>
      {hasMoreReviews && (
        <div className="mb-10 text-center">
          <button type="button" className="btn-ghost" onClick={() => setVisibleCount(count => count + 6)}>
            Load more reviews
          </button>
        </div>
      )}

      {myReview ? (
        <div className="card p-5 sm:p-8 bg-ocean-50 border-ocean-200">
          <h3 className="text-2xl mb-2">Thanks for your review!</h3>
          <p className="text-ocean-700">
            {myReview.pending
              ? "It's awaiting approval and will appear publicly soon."
              : "It's live for other guests to see."}
          </p>
        </div>
      ) : !user ? (
        <div className="card p-5 sm:p-8 text-center">
          <h3 className="text-2xl mb-2">Want to leave a review?</h3>
          <p className="text-ocean-700 mb-4">Log in to share your experience. Verified guests are approved automatically.</p>
          <Link to={`/login?next=/tours/${tourSlug}`} className="btn-primary">Log in to review</Link>
        </div>
      ) : checkingBooking ? (
        <div className="card p-5 sm:p-8">
          <h3 className="text-2xl mb-2">Checking your bookings…</h3>
          <p className="text-ocean-700">Review access is available for guests with a paid booking for this tour.</p>
        </div>
      ) : !hasPaidBooking ? (
        <div className="card p-5 sm:p-8 text-center">
          <h3 className="text-2xl mb-2">Reviews are for verified guests.</h3>
          <p className="text-ocean-700 mb-4">After you book and complete this tour, you can share your experience here.</p>
          <Link to={`/bookings`} className="btn-ghost">View my bookings</Link>
        </div>
      ) : (
        <div className="card p-5 sm:p-8">
          <h3 className="text-2xl mb-2">Leave a review</h3>
          <p className="text-ocean-700 text-sm mb-5">Your paid booking verifies this review, so it can appear for future guests.</p>
          {sent ? (
            <div className="rounded-xl bg-emerald-50 border border-emerald-200 p-5 text-emerald-900">
              <p className="font-semibold">Thanks for the review!</p>
              <p className="text-sm mt-1">Refresh the page if it doesn't show above.</p>
            </div>
          ) : (
            <form onSubmit={submit} className="space-y-4">
              <div>
                <label className="label" htmlFor="review-rating">Your rating</label>
                <StarInput value={form.rating} onChange={v => setForm(f => ({ ...f, rating: v }))} />
              </div>
              <div className="grid sm:grid-cols-2 gap-3">
                <div><label className="label" htmlFor="review-author-name">Your name *</label>
                  <input id="review-author-name" className="input" required value={form.author_name}
                    onChange={e => setForm({ ...form, author_name: e.target.value })} /></div>
                <div><label className="label" htmlFor="review-author-email">Email (private)</label>
                  <input id="review-author-email" type="email" className="input" value={form.author_email}
                    onChange={e => setForm({ ...form, author_email: e.target.value })} /></div>
              </div>
              <div>
                <label className="label" htmlFor="review-title">Title (optional)</label>
                <input
                  id="review-title"
                  className="input"
                  maxLength={REVIEW_TITLE_MAX}
                  value={form.title}
                  onChange={e => setForm({ ...form, title: e.target.value })}
                />
                <div className="mt-1 text-right text-xs text-ocean-500">
                  {form.title.length}/{REVIEW_TITLE_MAX}
                </div>
              </div>
              <div>
                <label className="label" htmlFor="review-body">Your review *</label>
                <textarea
                  id="review-body"
                  required
                  maxLength={REVIEW_BODY_MAX}
                  className="input min-h-[120px]"
                  value={form.body}
                  onChange={e => setForm({ ...form, body: e.target.value })} />
                <div className="mt-1 flex items-center justify-between gap-3 text-xs text-ocean-500">
                  <span>Maximum {REVIEW_BODY_MAX} characters.</span>
                  <span className={form.body.length > REVIEW_BODY_MAX * 0.9 ? "text-amber-700 font-semibold" : ""}>
                    {form.body.length}/{REVIEW_BODY_MAX}
                  </span>
                </div>
              </div>
              <div>
                <label className="label" htmlFor="review-photo">Photos (optional, up to 5)</label>
                <input
                  id="review-photo"
                  type="file"
                  accept="image/*"
                  multiple
                  className="input"
                  onChange={e => {
                    const selected = Array.from(e.target.files || []).slice(0, 5);
                    setPhotos(selected);
                    setErr((e.target.files?.length || 0) > 5 ? "Only the first 5 images will be uploaded." : "");
                  }}
                />
                {photos.length > 0 && <p className="text-xs text-ocean-500 mt-1">{photos.map(photo => photo.name).join(", ")}</p>}
              </div>
              {err && <p className="text-red-600 text-sm">{err}</p>}
              <button disabled={busy} className="btn-primary w-full sm:w-auto">
                {busy ? "Sending…" : "Submit review"}
              </button>
            </form>
          )}
        </div>
      )}
    </section>
  );
}
