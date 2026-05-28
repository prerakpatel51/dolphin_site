import { Link } from "react-router-dom";

const STYLE_CLASSES = {
  light: "bg-white text-ocean-950 border-ocean-100",
  ocean: "bg-ocean-700 text-white border-ocean-800",
  sunset: "bg-amber-50 text-ocean-950 border-amber-200",
  dark: "bg-ocean-950 text-white border-ocean-900",
};

export default function PageSections({ sections = [] }) {
  const activeSections = sections.filter(section => section?.title);
  if (!activeSections.length) return null;

  return (
    <div className="page-admin-sections">
      {activeSections.map(section => (
        <AdminSection key={section.id || `${section.title}-${section.sort_order}`} section={section} />
      ))}
    </div>
  );
}

function AdminSection({ section }) {
  const customStyle = {
    backgroundColor: section.background_color || undefined,
    color: section.text_color || undefined,
  };
  const className = STYLE_CLASSES[section.style] || STYLE_CLASSES.light;

  return (
    <section className={`border-y ${className}`} style={customStyle}>
      <div className="max-w-6xl mx-auto px-4 py-8 sm:py-10 grid md:grid-cols-[minmax(0,1fr)_280px] gap-6 items-center">
        <div>
          {section.eyebrow && (
            <p className="uppercase tracking-[0.24em] text-xs font-semibold opacity-75 mb-2">{section.eyebrow}</p>
          )}
          <h2 className="text-2xl sm:text-3xl font-display leading-tight">{section.title}</h2>
          {section.body && <p className="mt-3 text-base sm:text-lg opacity-85 max-w-3xl whitespace-pre-line">{section.body}</p>}
          {section.cta_label && section.cta_url && (
            <SectionLink to={section.cta_url} className="mt-5">
              {section.cta_label}
            </SectionLink>
          )}
        </div>
        {section.image_url && (
          <img
            src={section.image_url}
            alt={section.image_alt || ""}
            className="w-full aspect-[4/3] object-cover rounded-lg border border-white/30 shadow-lg shadow-ocean-950/10"
            loading="lazy"
          />
        )}
      </div>
    </section>
  );
}

function SectionLink({ to, className = "", children }) {
  const shared = `btn-primary ${className}`;
  if (to.startsWith("http") || to.startsWith("mailto:") || to.startsWith("tel:")) {
    return <a href={to} className={shared}>{children}</a>;
  }
  return <Link to={to} className={shared}>{children}</Link>;
}
