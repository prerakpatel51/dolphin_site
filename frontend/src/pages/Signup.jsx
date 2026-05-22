import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../lib/auth.jsx";

export default function Signup() {
  const { signup } = useAuth();
  const nav = useNavigate();
  const [f, setF] = useState({ email: "", password: "", first_name: "", last_name: "", phone: "", accepts_marketing: true });
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  async function submit(e) {
    e.preventDefault();
    if (!f.first_name.trim() || !f.last_name.trim()) {
      setErr("First name and last name are required.");
      return;
    }
    if (!/^\d{10}$/.test(f.phone)) {
      setErr("Phone number must be exactly 10 digits.");
      return;
    }
    setBusy(true); setErr("");
    try { await signup(f); nav("/"); }
    catch (e) { setErr(e.message); }
    finally { setBusy(false); }
  }

  const F = (k, label, type = "text") => (
    <div><label className="label">{label}</label>
      <input className="input" type={type} value={f[k]} onChange={e => setF({ ...f, [k]: e.target.value })} required={type !== "tel"} /></div>
  );

  const setPhone = (value) => setF({ ...f, phone: value.replace(/\D/g, "").slice(0, 10) });

  return (
    <div className="max-w-md mx-auto px-4 py-10 sm:py-16">
      <h1 className="text-3xl sm:text-4xl mb-6">Create an account</h1>
      <form onSubmit={submit} className="card p-6 sm:p-8 space-y-4">
        <div className="grid sm:grid-cols-2 gap-3">{F("first_name","First name")}{F("last_name","Last name")}</div>
        {F("email","Email","email")}
        <div>
          <label className="label">Phone</label>
          <input
            className="input"
            type="tel"
            inputMode="numeric"
            pattern="[0-9]{10}"
            maxLength={10}
            value={f.phone}
            onChange={e => setPhone(e.target.value)}
            required
          />
          <p className="mt-1 text-xs text-ocean-600">Numbers only, exactly 10 digits.</p>
        </div>
        <div>
          <label className="label">Password (min 8 chars)</label>
          <div className="relative">
            <input
              className="input pr-24"
              type={showPassword ? "text" : "password"}
              value={f.password}
              onChange={e => setF({ ...f, password: e.target.value })}
              minLength={8}
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
        <label className="flex items-start gap-3 text-sm text-ocean-800 cursor-pointer select-none pt-1">
          <input type="checkbox" checked={f.accepts_marketing}
            onChange={e => setF({ ...f, accepts_marketing: e.target.checked })}
            className="mt-1 w-4 h-4 accent-ocean-600" />
          <span>Email me deals, promo codes, and tour updates. Unsubscribe anytime in account settings.</span>
        </label>
        {err && <p className="text-red-600 text-sm">{err}</p>}
        <button disabled={busy} className="btn-primary w-full">{busy ? "…" : "Sign up"}</button>
        <p className="text-sm text-ocean-700 text-center">Have an account? <Link to="/login" className="underline">Login</Link></p>
      </form>
    </div>
  );
}
