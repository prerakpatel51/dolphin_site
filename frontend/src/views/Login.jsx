"use client";

import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../lib/auth.jsx";
import SEO from "../components/SEO.jsx";
import { useSite } from "../lib/site.js";

export default function Login() {
  const { site, page } = useSite("login");
  const { login } = useAuth();
  const nav = useNavigate();
  const [params] = useSearchParams();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setBusy(true); setErr("");
    try {
      await login(email.trim(), password);
      const nextPath = params.get("next");
      const safeNext = (nextPath && nextPath.startsWith("/") && !nextPath.startsWith("//")) ? nextPath : "/";
      nav(safeNext);
    } catch (e) { setErr("Invalid email or password."); }
    finally { setBusy(false); }
  }

  return (
    <div className="max-w-md mx-auto px-4 py-10 sm:py-16">
      <SEO
        title={page.seo_title || `Login | ${site.site_name}`}
        description={page.seo_description || "Log in to your Dolphin Island Tours account to manage bookings and trip details."}
        canonical="/login"
        robots="noindex, follow"
      />
      {page.hero_eyebrow && <p className="uppercase tracking-[0.24em] text-ocean-500 text-xs mb-2">{page.hero_eyebrow}</p>}
      <h1 className="text-3xl sm:text-4xl mb-3">{page.hero_title || "Welcome back"}</h1>
      {page.hero_subtitle && <p className="text-ocean-700 mb-6">{page.hero_subtitle}</p>}
      {page.intro_eyebrow && <p className="text-sm font-semibold text-ocean-600 mb-2">{page.intro_eyebrow}</p>}
      {page.intro_body && <p className="text-ocean-700 mb-6">{page.intro_body}</p>}
      <form onSubmit={submit} className="card p-6 sm:p-8 space-y-4">
        <div><label className="label" htmlFor="login-email">Email</label>
          <input id="login-email" className="input" type="email" value={email} onChange={e=>setEmail(e.target.value)} required /></div>
        <div>
          <label className="label" htmlFor="login-password">Password</label>
          <div className="relative">
            <input
              id="login-password"
              className="input pr-24"
              type={showPassword ? "text" : "password"}
              value={password}
              onChange={e=>setPassword(e.target.value)}
              required
            />
            <button
              type="button"
              onClick={() => setShowPassword(v => !v)}
              className="absolute right-2 top-1/2 -translate-y-1/2 rounded-md px-3 py-1.5 text-sm font-semibold text-ocean-700 hover:bg-ocean-50"
            >
              {showPassword ? "Hide" : "Show"}
            </button>
          </div>
        </div>
        {err && <p className="text-red-600 text-sm">{err}</p>}
        <button disabled={busy} className="btn-primary w-full">{busy ? "…" : "Login"}</button>
        <div className="flex items-center justify-between text-sm text-ocean-700">
          <Link to="/forgot-password" className="underline">Forgot password?</Link>
          <Link to="/signup" className="underline">No account? Sign up</Link>
        </div>
      </form>
    </div>
  );
}
