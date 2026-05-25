import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { api } from "../lib/api.js";
import SEO from "../components/SEO.jsx";

export default function ResetPassword() {
  const nav = useNavigate();
  const [params] = useSearchParams();
  const uid = params.get("uid") || "";
  const token = params.get("token") || "";
  const [pw, setPw] = useState("");
  const [pw2, setPw2] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const [done, setDone] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setErr("");
    if (pw.length < 8) { setErr("Password must be at least 8 characters."); return; }
    if (pw !== pw2) { setErr("Passwords don't match."); return; }
    setBusy(true);
    try {
      await api.passwordResetConfirm({ uid, token, password: pw });
      setDone(true);
      setTimeout(() => nav("/login"), 1800);
    } catch (e) { setErr(e.message); }
    finally { setBusy(false); }
  }

  if (!uid || !token) {
    return (
      <div className="max-w-md mx-auto px-4 py-16 text-center">
        <SEO
          title="Reset Link Missing | Dolphin Island Tours"
          description="Request a new Dolphin Island Tours password reset link."
          canonical="/forgot-password"
          robots="noindex, follow"
        />
        <h1 className="text-3xl mb-2">Reset link is missing.</h1>
        <p className="text-ocean-700 mb-6">Request a new one.</p>
        <Link to="/forgot-password" className="btn-primary">Send new link</Link>
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto px-4 py-10 sm:py-16">
      <SEO
        title="Set a New Password | Dolphin Island Tours"
        description="Set a new password for your Dolphin Island Tours account."
        canonical="/reset-password"
        robots="noindex, follow"
      />
      <h1 className="text-3xl sm:text-4xl mb-2">Set a new password</h1>
      <div className="card p-6 sm:p-8 mt-6">
        {done ? (
          <div className="rounded-xl bg-emerald-50 border border-emerald-200 p-5 text-emerald-900">
            <p className="font-semibold">Password updated.</p>
            <p className="text-sm mt-1">Redirecting to login…</p>
          </div>
        ) : (
          <form onSubmit={submit} className="space-y-4">
            <div><label className="label" htmlFor="reset-password">New password</label>
              <input id="reset-password" type="password" required minLength={8} className="input"
                value={pw} onChange={e => setPw(e.target.value)} /></div>
            <div><label className="label" htmlFor="reset-password-confirm">Confirm new password</label>
              <input id="reset-password-confirm" type="password" required minLength={8} className="input"
                value={pw2} onChange={e => setPw2(e.target.value)} /></div>
            {err && <p className="text-red-600 text-sm">{err}</p>}
            <button disabled={busy} className="btn-primary w-full">{busy ? "…" : "Update password"}</button>
          </form>
        )}
      </div>
    </div>
  );
}
