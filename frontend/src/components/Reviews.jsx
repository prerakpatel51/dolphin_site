import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api.js";
import { useAuth } from "../lib/auth.jsx";
import { Stars, StarInput } from "./Stars.jsx";

const REVIEW_TITLE_MAX = 80;
const REVIEW_BODY_MAX = 1000;

export default function Reviews({ tourSlug }) {
  const { user } = useAuth();
  const [reviews, setReviews] = useState([]);
  const [stats, setStats] = useState({ count: 0, average: 0, breakdown: {} });
  const [form, setForm] = useState({ author_name: "", author_email: "", rating: 5, title: "", body: "" });
  const [sent, setSent] = useState(false);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  useEffect(() => {
    api.reviews({ tour: tourSlug }).then(d => setReviews(d.results || d));
    if (tourSlug) api.reviewStats(tourSlug).then(setStats);
    if (user) setForm(f => ({
      ...f,
      author_name: `${user.first_name || ""} ${user.last_name || ""}`.trim() || user.username,
      author_email: user.email,
    }));
  }, [tourSlug, user]);

  const myReview = user ? reviews.find(r => r.mine) : null;

  async function submit(e) {
    e.preventDefault();
    setBusy(true); setErr("");
    try {
      const res = await api.submitReview({ ...form, tour_slug: tourSlug });
      setSent(true);
      if (res?.review) setReviews(r => [res.review, ...r.filter(x => x.id !== res.review.id)]);
    } catch (e) { setErr(e.message); }
    finally { setBusy(false); }
  }

  return (
    <section className="mt-12 sm:mt-16">
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

      <div className="grid md:grid-cols-2 gap-4 sm:gap-6 mb-10">
        {reviews.length === 0 && <p className="text-ocean-600 col-span-full">No reviews yet — be the first!</p>}
        {reviews.slice(0, 6).map(r => (
          <article key={r.id} className={`card p-5 sm:p-6 ${r.pending ? "border-amber-300 bg-amber-50/40" : ""}`}>
            <div className="flex items-start justify-between gap-3">
              <Stars value={r.rating} />
              {r.mine && (
                <span className="text-[10px] uppercase tracking-wider rounded-full bg-ocean-100 text-ocean-800 px-2 py-0.5 font-semibold">Your review</span>
              )}
              {r.pending && (
                <span className="text-[10px] uppercase tracking-wider rounded-full bg-amber-200 text-amber-900 px-2 py-0.5 font-semibold">Pending</span>
              )}
            </div>
            {r.title && <h3 className="text-lg mt-2">{r.title}</h3>}
            <p className="text-ocean-800 mt-2 leading-relaxed whitespace-pre-line">{r.body}</p>
            <p className="text-sm text-ocean-500 mt-4">— {r.author_name} · {new Date(r.created_at).toLocaleDateString()}</p>
          </article>
        ))}
      </div>

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
      ) : (
        <div className="card p-5 sm:p-8">
          <h3 className="text-2xl mb-2">Leave a review</h3>
          <p className="text-ocean-700 text-sm mb-5">Verified bookings are auto-approved. Others are reviewed before publishing.</p>
          {sent ? (
            <div className="rounded-xl bg-emerald-50 border border-emerald-200 p-5 text-emerald-900">
              <p className="font-semibold">Thanks for the review!</p>
              <p className="text-sm mt-1">Refresh the page if it doesn't show above.</p>
            </div>
          ) : (
            <form onSubmit={submit} className="space-y-4">
              <div>
                <label className="label">Your rating</label>
                <StarInput value={form.rating} onChange={v => setForm(f => ({ ...f, rating: v }))} />
              </div>
              <div className="grid sm:grid-cols-2 gap-3">
                <div><label className="label">Your name *</label>
                  <input className="input" required value={form.author_name}
                    onChange={e => setForm({ ...form, author_name: e.target.value })} /></div>
                <div><label className="label">Email (private)</label>
                  <input type="email" className="input" value={form.author_email}
                    onChange={e => setForm({ ...form, author_email: e.target.value })} /></div>
              </div>
              <div>
                <label className="label">Title (optional)</label>
                <input
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
                <label className="label">Your review *</label>
                <textarea
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
