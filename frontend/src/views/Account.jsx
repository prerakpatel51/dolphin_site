"use client";

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../lib/auth.jsx";
import { api } from "../lib/api.js";
import SEO from "../components/SEO.jsx";

export default function Account() {
  const { user, loading, deleteAccount, refresh } = useAuth();
  const nav = useNavigate();
  const [f, setF] = useState({
    first_name: user?.first_name || "",
    last_name: user?.last_name || "",
    phone: user?.phone || "",
    accepts_marketing: !!user?.accepts_marketing,
  });
  const [msg, setMsg] = useState("");
  const [err, setErr] = useState("");

  useEffect(() => {
    if (!user) return;
    setF({
      first_name: user.first_name || "",
      last_name: user.last_name || "",
      phone: user.phone || "",
      accepts_marketing: !!user.accepts_marketing,
    });
  }, [user]);

  useEffect(() => {
    if (!loading && !user) nav("/login");
  }, [loading, nav, user]);

  if (loading) {
    return (
      <div className="max-w-xl mx-auto px-4 py-10 sm:py-16">
        <SEO
          title="Account | Dolphin Island Tours"
          description="Manage your Dolphin Island Tours account details."
          canonical="/account"
          robots="noindex, follow"
        />
        <h1 className="text-3xl sm:text-4xl mb-6">Account</h1>
        <div className="card p-6 sm:p-8 text-ocean-700">Loading account…</div>
      </div>
    );
  }

  if (!user) return null;

  async function save(e) {
    e.preventDefault();
    setMsg("");
    setErr("");
    if (!f.first_name.trim() || !f.last_name.trim()) {
      setErr("First name and last name are required.");
      return;
    }
    if (!/^\d{10}$/.test(f.phone)) {
      setErr("Phone number must be exactly 10 digits.");
      return;
    }
    try {
      await api.updateMe(f);
      await refresh();
      setMsg("Saved.");
    } catch (e) {
      setErr(e.message);
    }
  }
  async function destroy() {
    if (!confirm("Permanently delete your account and all data?")) return;
    await deleteAccount();
    nav("/");
  }
  const setPhone = (value) => setF({ ...f, phone: value.replace(/\D/g, "").slice(0, 10) });

  return (
    <div className="max-w-xl mx-auto px-4 py-10 sm:py-16">
      <SEO
        title="Account | Dolphin Island Tours"
        description="Manage your Dolphin Island Tours account details and marketing email preferences."
        canonical="/account"
        robots="noindex, follow"
      />
      <h1 className="text-3xl sm:text-4xl mb-6">Account</h1>
      <form onSubmit={save} className="card p-6 sm:p-8 space-y-4">
        <div><label className="label" htmlFor="account-email">Email</label><input id="account-email" disabled className="input bg-ocean-50 break-all" value={user.email} /></div>
        <div className="grid sm:grid-cols-2 gap-3">
          <div><label className="label" htmlFor="account-first-name">First name</label><input id="account-first-name" className="input" value={f.first_name} onChange={e=>setF({...f,first_name:e.target.value})} required /></div>
          <div><label className="label" htmlFor="account-last-name">Last name</label><input id="account-last-name" className="input" value={f.last_name} onChange={e=>setF({...f,last_name:e.target.value})} required /></div>
        </div>
        <div>
          <label className="label" htmlFor="account-phone">Phone</label>
          <input
            id="account-phone"
            className="input"
            type="tel"
            inputMode="numeric"
            pattern="[0-9]{10}"
            maxLength={10}
            value={f.phone}
            onChange={e=>setPhone(e.target.value)}
            required
          />
          <p className="mt-1 text-xs text-ocean-600">Numbers only, exactly 10 digits.</p>
        </div>
        <div className="border-t border-ocean-100 pt-4">
          <label className="flex items-start gap-3 text-sm text-ocean-800 cursor-pointer select-none">
            <input type="checkbox" checked={f.accepts_marketing}
              onChange={e=>setF({...f,accepts_marketing:e.target.checked})}
              className="mt-1 w-4 h-4 accent-ocean-600" />
            <span>
              <b>Marketing emails</b><br/>
              <span className="text-ocean-600">Email me deals, promo codes, and tour updates. Booking receipts always sent.</span>
            </span>
          </label>
        </div>
        <button className="btn-primary w-full">Save</button>
        {err && <p className="text-red-600 text-sm">{err}</p>}
        {msg && <p className="text-emerald-700 text-sm">{msg}</p>}
      </form>

      <div className="card p-6 sm:p-8 mt-6 sm:mt-8 border-red-200">
        <h3 className="text-xl text-red-700 mb-2">Danger zone</h3>
        <p className="text-ocean-700 text-sm mb-4">Deleting your account also cancels your active bookings.</p>
        <button onClick={destroy} className="btn !bg-red-600 !text-white hover:!bg-red-700">Delete account</button>
      </div>
    </div>
  );
}
