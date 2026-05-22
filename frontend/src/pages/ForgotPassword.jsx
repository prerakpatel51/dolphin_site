import { useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api.js";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  async function submit(e) {
    e.preventDefault();
    setBusy(true); setErr("");
    try { await api.passwordResetRequest(email); setSent(true); }
    catch (e) { setErr(e.message); }
    finally { setBusy(false); }
  }

  return (
    <div className="max-w-md mx-auto px-4 py-10 sm:py-16">
      <h1 className="text-3xl sm:text-4xl mb-2">Forgot your password?</h1>
      <p className="text-ocean-700 mb-6">Enter your email — we'll send a reset link.</p>
      <div className="card p-6 sm:p-8">
        {sent ? (
          <div className="rounded-xl bg-emerald-50 border border-emerald-200 p-5 text-emerald-900">
            <p className="font-semibold">Check your inbox.</p>
            <p className="text-sm mt-1">If an account exists for {email}, we sent a reset link. It expires in 24 hours.</p>
          </div>
        ) : (
          <form onSubmit={submit} className="space-y-4">
            <div>
              <label className="label">Email</label>
              <input className="input" type="email" required value={email}
                onChange={e => setEmail(e.target.value)} />
            </div>
            {err && <p className="text-red-600 text-sm">{err}</p>}
            <button disabled={busy} className="btn-primary w-full">{busy ? "…" : "Send reset link"}</button>
            <p className="text-sm text-ocean-700 text-center">
              Remembered it? <Link to="/login" className="underline">Back to login</Link>
            </p>
          </form>
        )}
      </div>
    </div>
  );
}
