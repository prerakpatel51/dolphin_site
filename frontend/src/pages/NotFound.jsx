import { Link } from "react-router-dom";
import SEO from "../components/SEO.jsx";

export default function NotFound() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-16 sm:py-24 text-center">
      <SEO
        title="Page Not Found | Dolphin Island Tours"
        description="The Dolphin Island Tours page you requested could not be found. Browse current tours or contact us for help."
        canonical="/404"
        robots="noindex, follow"
      />
      <p className="uppercase tracking-[0.18em] text-ocean-500 text-xs mb-2">404</p>
      <h1 className="text-3xl sm:text-5xl mb-3">Page not found.</h1>
      <p className="text-ocean-700 mb-6">
        The page may have moved, or the link may be out of date.
      </p>
      <div className="flex flex-col sm:flex-row gap-3 justify-center">
        <Link className="btn-primary" to="/tours">Browse tours</Link>
        <Link className="btn-ghost" to="/contact">Contact us</Link>
      </div>
    </div>
  );
}
