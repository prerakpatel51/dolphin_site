import { useState } from "react";
import { api } from "../lib/api.js";
import { useSite } from "../lib/site.js";
import { breadcrumbJsonLd, graphJsonLd, localBusinessJsonLd } from "../lib/seo.js";
import SEO from "../components/SEO.jsx";

export default function Contact() {
  const [f, setF] = useState({ name: "", email: "", phone: "", subject: "", message: "" });
  const [sent, setSent] = useState(false);
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);
  const { site, page } = useSite("contact");

  async function submit(e) {
    e.preventDefault();
    setBusy(true); setErr("");
    try { await api.contact(f); setSent(true); }
    catch (e) { setErr(e.message); }
    finally { setBusy(false); }
  }

  return (
    <div>
      <SEO
        title={page.seo_title || "Contact - Dolphin Island Tours"}
        description={page.seo_description}
        keywords={page.seo_keywords}
        image={page.hero_image_url}
        canonical="/contact"
        jsonLd={graphJsonLd([
          localBusinessJsonLd(site, page.hero_image_url || "/images/lagoon.jpg"),
          breadcrumbJsonLd([{ name: "Home", path: "/" }, { name: "Contact", path: "/contact" }]),
        ])}
      />
      <section className="relative h-[30vh] min-h-[220px] overflow-hidden">
        <img src={page.hero_image_url || "/images/lagoon.jpg"} alt="" className="absolute inset-0 w-full h-full object-cover" />
        <div className="absolute inset-0 bg-ocean-950/60" />
        <div className="relative max-w-4xl mx-auto px-4 h-full flex flex-col justify-end pb-8 sm:pb-10 text-white">
          <p className="uppercase tracking-[0.25em] sm:tracking-[0.3em] text-ocean-200 text-[10px] sm:text-xs mb-2 sm:mb-3">{page.hero_eyebrow}</p>
          <h1 className="text-3xl sm:text-5xl lg:text-6xl font-display leading-[1.1]">{page.hero_title}</h1>
        </div>
      </section>

      <div className="max-w-5xl mx-auto px-4 py-10 sm:py-16 grid md:grid-cols-5 gap-8 sm:gap-10">
        <div className="md:col-span-2">
          <h2 className="text-2xl mb-3">{page.section_one_title}</h2>
          <p className="text-ocean-700 mb-6">{page.section_one_body}</p>
          <ul className="space-y-3 text-ocean-800">
            <li><b>Email:</b> <a className="underline" href={`mailto:${site.contact_email}`}>{site.contact_email}</a></li>
            {site.contact_phone && <li><b>Phone:</b> <a className="underline" href={`tel:${site.contact_phone}`}>{site.contact_phone}</a></li>}
            <li><b>Visit:</b> {site.address}</li>
            <li><b>Hours:</b> {site.hours}</li>
          </ul>
          <div className="rounded-2xl overflow-hidden mt-6 aspect-[4/3] border border-ocean-100">
            <iframe title="Map" className="w-full h-full"
              src={site.map_embed_url}
              loading="lazy" referrerPolicy="no-referrer-when-downgrade" />
          </div>
        </div>

        <form onSubmit={submit} className="card p-5 sm:p-8 md:col-span-3 space-y-4 h-fit">
          <h2 className="text-2xl">{page.section_two_title}</h2>
          {sent ? (
            <div className="rounded-xl bg-emerald-50 border border-emerald-200 p-5 text-emerald-900">
              <p className="font-semibold">{page.cta_title}</p>
              <p className="text-sm mt-1">{page.cta_body}</p>
            </div>
          ) : (
            <>
              <div className="grid sm:grid-cols-2 gap-3">
                <div><label className="label">Your name *</label>
                  <input className="input" required value={f.name} onChange={e=>setF({...f,name:e.target.value})}/></div>
                <div><label className="label">Email *</label>
                  <input type="email" className="input" required value={f.email} onChange={e=>setF({...f,email:e.target.value})}/></div>
                <div><label className="label">Phone</label>
                  <input className="input" value={f.phone} onChange={e=>setF({...f,phone:e.target.value})}/></div>
                <div><label className="label">Subject</label>
                  <input className="input" value={f.subject} onChange={e=>setF({...f,subject:e.target.value})} placeholder="Booking question, private charter…"/></div>
              </div>
              <div><label className="label">Your message *</label>
                <textarea required className="input min-h-[160px]" value={f.message} onChange={e=>setF({...f,message:e.target.value})}/></div>
              {err && <p className="text-red-600 text-sm">{err}</p>}
              <button disabled={busy} className="btn-primary w-full">{busy ? "Sending…" : "Send message"}</button>
              <p className="text-xs text-ocean-500">By submitting, you agree to be contacted about your inquiry.</p>
            </>
          )}
        </form>
      </div>
    </div>
  );
}
