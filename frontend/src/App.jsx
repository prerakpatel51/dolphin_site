import { Routes, Route, Link, NavLink, useLocation, useNavigate } from "react-router-dom";
import { Suspense, lazy, useEffect, useState } from "react";
import { useAuth } from "./lib/auth.jsx";
import { imageFrom, useSite } from "./lib/site.js";
import { initMarketingTags, trackPageView } from "./lib/tracking.js";
import PageSections from "./components/PageSections.jsx";

const routeLoaders = {
  home: () => import("./pages/Home.jsx"),
  tours: () => import("./pages/Tours.jsx"),
  tourDetail: () => import("./pages/TourDetail.jsx"),
  book: () => import("./pages/Book.jsx"),
  login: () => import("./pages/Login.jsx"),
  signup: () => import("./pages/Signup.jsx"),
  account: () => import("./pages/Account.jsx"),
  bookings: () => import("./pages/MyBookings.jsx"),
  about: () => import("./pages/About.jsx"),
  contact: () => import("./pages/Contact.jsx"),
  reviews: () => import("./pages/ReviewsPage.jsx"),
  forgotPassword: () => import("./pages/ForgotPassword.jsx"),
  resetPassword: () => import("./pages/ResetPassword.jsx"),
  notFound: () => import("./pages/NotFound.jsx"),
};

const Home = lazy(routeLoaders.home);
const Tours = lazy(routeLoaders.tours);
const TourDetail = lazy(routeLoaders.tourDetail);
const Book = lazy(routeLoaders.book);
const Login = lazy(routeLoaders.login);
const Signup = lazy(routeLoaders.signup);
const Account = lazy(routeLoaders.account);
const MyBookings = lazy(routeLoaders.bookings);
const About = lazy(routeLoaders.about);
const Contact = lazy(routeLoaders.contact);
const ReviewsPage = lazy(routeLoaders.reviews);
const ForgotPassword = lazy(routeLoaders.forgotPassword);
const ResetPassword = lazy(routeLoaders.resetPassword);
const NotFound = lazy(routeLoaders.notFound);

function preloadRoute(key) {
  routeLoaders[key]?.();
}

export default function App() {
  const { user, logout } = useAuth();
  const { site } = useSite("home");
  const nav = useNavigate();
  const location = useLocation();
  const { page: currentPage } = useSite(pageKeyFromPath(location.pathname));
  const logo = imageFrom(site, "logo", "/images/logo.png");
  const [open, setOpen] = useState(false);
  useEffect(() => { initMarketingTags(site); }, [site]);
  useEffect(() => {
    trackPageView(site, `${location.pathname}${location.search}`);
  }, [site, location.pathname, location.search]);
  useEffect(() => { setOpen(false); }, [location.pathname]);

  async function handleLogout() {
    try {
      await logout();
      nav("/");
    } catch (err) {
      console.error("Logout failed", err);
    }
  }

  return (
    <div className="min-h-screen flex flex-col bg-ocean-50 text-ocean-950">
      <header className="sticky top-0 z-40 backdrop-blur-xl bg-white/90 border-b border-ocean-100/80 shadow-sm shadow-ocean-900/5">
        <div className="max-w-6xl mx-auto px-4 h-16 sm:h-[72px] flex items-center justify-between">
          <Link to="/" onClick={() => setOpen(false)} className="flex items-center gap-2 sm:gap-3 min-w-0">
            <img src={logo} alt={site.site_name} className="h-9 sm:h-10 w-auto" />
            <span className="hidden sm:block font-display text-base sm:text-lg text-ocean-800 truncate">{site.site_name}</span>
          </Link>
          <nav className="hidden md:flex items-center gap-1 lg:gap-3 text-sm">
            <NavItem to="/tours" preloadKey="tours">Tours</NavItem>
            <NavItem to="/reviews" preloadKey="reviews">Reviews</NavItem>
            <NavItem to="/about" preloadKey="about">About</NavItem>
            <NavItem to="/contact" preloadKey="contact">Contact</NavItem>
            {user ? (
              <>
                <NavItem to="/bookings" preloadKey="bookings">My Bookings</NavItem>
                <NavItem to="/account" preloadKey="account">Account</NavItem>
                <button onClick={handleLogout} className="text-ocean-700 hover:text-ocean-900 px-2">Logout</button>
              </>
            ) : (
              <>
                <NavItem to="/login" preloadKey="login">Login</NavItem>
                <Link to="/signup" onMouseEnter={() => preloadRoute("signup")} onFocus={() => preloadRoute("signup")} className="btn-primary !py-2 !px-4 text-sm">Sign up</Link>
              </>
            )}
          </nav>
          <button onClick={() => setOpen(o => !o)} aria-label="Menu"
            className="md:hidden w-10 h-10 rounded-full hover:bg-ocean-100 flex items-center justify-center">
            <span className="relative w-5 h-4">
              <span className={`absolute left-0 right-0 h-0.5 bg-ocean-800 transition-transform ${open ? "top-1.5 rotate-45" : "top-0"}`} />
              <span className={`absolute left-0 right-0 h-0.5 bg-ocean-800 top-1.5 transition-opacity ${open ? "opacity-0" : "opacity-100"}`} />
              <span className={`absolute left-0 right-0 h-0.5 bg-ocean-800 transition-transform ${open ? "top-1.5 -rotate-45" : "top-3"}`} />
            </span>
          </button>
        </div>
        {open && (
          <div className="md:hidden border-t border-ocean-100 bg-white shadow-2xl shadow-ocean-950/10">
            <nav className="px-4 py-4 flex flex-col gap-1 text-base">
              <MItem to="/tours" preloadKey="tours" onClick={() => setOpen(false)}>Tours</MItem>
              <MItem to="/reviews" preloadKey="reviews" onClick={() => setOpen(false)}>Reviews</MItem>
              <MItem to="/about" preloadKey="about" onClick={() => setOpen(false)}>About</MItem>
              <MItem to="/contact" preloadKey="contact" onClick={() => setOpen(false)}>Contact</MItem>
              {user ? (
                <>
                  <MItem to="/bookings" preloadKey="bookings" onClick={() => setOpen(false)}>My Bookings</MItem>
                  <MItem to="/account" preloadKey="account" onClick={() => setOpen(false)}>Account</MItem>
                  <button onClick={async () => {
                    setOpen(false);
                    await handleLogout();
                  }}
                    className="text-left px-4 py-3 rounded-xl text-ocean-700 hover:bg-ocean-50">Logout</button>
                </>
              ) : (
                <>
                  <MItem to="/login" preloadKey="login" onClick={() => setOpen(false)}>Login</MItem>
                  <Link to="/signup" onMouseEnter={() => preloadRoute("signup")} onFocus={() => preloadRoute("signup")} onClick={() => setOpen(false)} className="btn-primary mt-2 text-base">Sign up</Link>
                </>
              )}
            </nav>
          </div>
        )}
      </header>

      <main className="flex-1">
        <PageSections sections={currentPage.sections || []} />
        <Suspense fallback={<RouteFallback />}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/tours" element={<Tours />} />
            <Route path="/reviews" element={<ReviewsPage />} />
            <Route path="/tours/:slug" element={<TourDetail />} />
            <Route path="/book/:slug" element={<Book />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/account" element={<Account />} />
            <Route path="/bookings" element={<MyBookings />} />
            <Route path="/about" element={<About />} />
            <Route path="/contact" element={<Contact />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password" element={<ResetPassword />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Suspense>
      </main>

      <footer className="bg-ocean-950 text-ocean-100 mt-16 sm:mt-20">
        <div className="max-w-6xl mx-auto px-4 py-10 sm:py-12 grid sm:grid-cols-3 gap-8 sm:gap-10">
          <div>
            <div className="inline-flex bg-white rounded-md p-1.5 mb-3">
              <img src={logo} alt="" className="h-10 sm:h-12 w-auto" />
            </div>
            <p className="text-ocean-200 text-sm">{site.tagline}</p>
          </div>
          <div>
            <h4 className="font-semibold mb-2">Visit</h4>
            <p className="text-sm text-ocean-200">{site.address}</p>
            <p className="text-sm text-ocean-200 mt-2">{site.hours}</p>
          </div>
          <div>
            <h4 className="font-semibold mb-2">Contact</h4>
            <a className="block text-sm text-ocean-200 hover:text-white break-all" href={`mailto:${site.contact_email}`}>{site.contact_email}</a>
            {site.contact_phone && <a className="block text-sm text-ocean-200 hover:text-white mt-2" href={`tel:${site.contact_phone}`}>{site.contact_phone}</a>}
            <Link to="/contact" className="block text-sm text-ocean-200 hover:text-white mt-2 underline">Send a message →</Link>

            <div className="mt-6 flex gap-4">
              {site.facebook_url && <a href={site.facebook_url} target="_blank" rel="noreferrer" className="text-ocean-300 hover:text-white transition-colors" aria-label="Facebook"><FacebookIcon /></a>}
              {site.instagram_url && <a href={site.instagram_url} target="_blank" rel="noreferrer" className="text-ocean-300 hover:text-white transition-colors" aria-label="Instagram"><InstagramIcon /></a>}
              {site.youtube_url && <a href={site.youtube_url} target="_blank" rel="noreferrer" className="text-ocean-300 hover:text-white transition-colors" aria-label="YouTube"><YouTubeIcon /></a>}
              {site.tiktok_url && <a href={site.tiktok_url} target="_blank" rel="noreferrer" className="text-ocean-300 hover:text-white transition-colors" aria-label="TikTok"><TikTokIcon /></a>}
            </div>
          </div>
        </div>
        <div className="text-center text-xs text-ocean-300 py-4 border-t border-ocean-800">
          &copy; {new Date().getFullYear()} {site.site_name}
        </div>
      </footer>
    </div>
  );
}

function FacebookIcon() {
  return (
    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path fillRule="evenodd" d="M22 12c0-5.523-4.477-10-10-10S2 6.477 2 12c0 4.991 3.657 9.128 8.438 9.878v-6.987h-2.54V12h2.54V9.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V12h2.773l-.443 2.89h-2.33v6.988C18.343 21.128 22 16.991 22 12z" clipRule="evenodd" />
    </svg>
  );
}

function InstagramIcon() {
  return (
    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path fillRule="evenodd" d="M12.315 2c2.43 0 2.784.013 3.808.06 1.064.049 1.791.218 2.427.465a4.902 4.902 0 011.772 1.153 4.902 4.902 0 011.153 1.772c.247.636.416 1.363.465 2.427.048 1.067.06 1.407.06 4.123v.08c0 2.643-.012 2.987-.06 4.043-.049 1.064-.218 1.791-.465 2.427a4.902 4.902 0 01-1.153 1.772 4.902 4.902 0 01-1.772 1.153c-.636.247-1.363.416-2.427.465-1.067.048-1.407.06-4.123.06h-.08c-2.643 0-2.987-.012-4.043-.06-1.064-.049-1.791-.218-2.427-.465a4.902 4.902 0 01-1.772-1.153 4.902 4.902 0 01-1.153-1.772c-.247-.636-.416-1.363-.465-2.427-.047-1.024-.06-1.379-.06-3.808v-.63c0-2.43.013-2.784.06-3.808.049-1.064.218-1.791.465-2.427a4.902 4.902 0 011.153-1.772A4.902 4.902 0 015.45 2.525c.636-.247 1.363-.416 2.427-.465C8.901 2.013 9.256 2 11.685 2h.63zm-.081 1.802h-.468c-2.456 0-2.784.011-3.807.058-.975.045-1.504.207-1.857.344-.467.182-.8.398-1.15.748-.35.35-.566.683-.748 1.15-.137.353-.3.882-.344 1.857-.047 1.023-.058 1.351-.058 3.807v.468c0 2.456.011 2.784.058 3.807.045.975.207 1.504.344 1.857.182.466.399.8.748 1.15.35.35.683.566 1.15.748.353.137.882.3 1.857.344 1.054.048 1.37.058 4.041.058h.08c2.597 0 2.917-.01 3.96-.058.976-.045 1.505-.207 1.858-.344.466-.182.8-.398 1.15-.748.35-.35.566-.683.748-1.15.137-.353.3-.882.344-1.857.048-1.055.058-1.37.058-4.041v-.08c0-2.597-.01-2.917-.058-3.96-.045-.976-.207-1.505-.344-1.858a3.097 3.097 0 00-.748-1.15 3.098 3.098 0 00-1.15-.748c-.353-.137-.882-.3-1.857-.344-1.023-.047-1.351-.058-3.807-.058zM12 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16.36a4.198 4.198 0 110-8.396 4.198 4.198 0 010 8.396zm5.33-9.307a1.2 1.2 0 11-2.401 0 1.2 1.2 0 012.401 0z" clipRule="evenodd" />
    </svg>
  );
}

function YouTubeIcon() {
  return (
    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path fillRule="evenodd" d="M19.615 3.184c-3.604-.246-11.631-.245-15.23 0-3.897.266-4.356 2.62-4.385 8.816.029 6.185.484 8.549 4.385 8.816 3.6.245 11.626.246 15.23 0 3.897-.266 4.356-2.62 4.385-8.816-.029-6.185-.484-8.549-4.385-8.816zm-10.615 12.816v-8l8 4-8 4z" clipRule="evenodd" />
    </svg>
  );
}

function TikTokIcon() {
  return (
    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12.525.02c1.31 0 2.568.354 3.648 1.012.01.006.01.01.017.017.012.008.02.012.028.02a1 1 0 01.164.137c.01.01.02.02.03.03.01.012.022.024.032.037l.017.02c.01.014.02.03.03.045.006.01.012.02.017.03.01.016.02.033.028.05.004.01.008.018.012.027a1 1 0 01.022.052c.004.01.007.02.01.03.007.02.013.042.02.064.002.008.004.016.006.024.005.023.01.047.014.07.002.01.003.017.005.026.003.024.006.048.008.073v.032c.002.024.004.048.004.072V5.01a5.5 5.5 0 003.62-1.39l.024-.022.023-.024.02-.018c.013-.01.026-.02.04-.03a.5.5 0 01.042-.03.55.55 0 01.045-.028c.015-.01.03-.017.045-.025l.044-.022.047-.02c.016-.006.03-.01.048-.016l.048-.013c.017-.005.035-.01.053-.013l.05-.01c.018-.002.037-.005.056-.007l.053-.003.056-.002c.02 0 .04 0 .06.002h.023c.02 0 .04.003.06.005h.016c.023.003.046.007.068.01l.015.004.06.01c.024.005.048.012.072.018l.008.003c.024.006.047.014.07.02l.012.004c.023.008.046.017.068.026l.01.005c.025.01.05.02.074.03l.005.003a3.5 3.5 0 01.08.037l.003.002c.02.01.04.022.06.033l.012.007c.023.013.045.028.067.043l.006.004c.02.015.04.03.06.047l.008.007c.018.016.035.033.05.05l.012.01c.016.017.03.036.044.054l.005.006a3.5 3.5 0 01.043.06v.003c.012.02.024.04.035.06l.007.013c.01.022.02.044.03.067l.003.007a3.5 3.5 0 01.024.073l.004.015c.007.025.013.05.018.075v.004a3.5 3.5 0 01.01.077c.003.023.005.047.006.072v.013c.002.026.003.052.003.078v.02c0 .02 0 .04-.003.06l-.001.013c-.002.026-.004.05-.008.076l-.004.018c-.005.024-.01.048-.016.072l-.006.02c-.007.024-.015.047-.024.07l-.006.017c-.01.025-.022.05-.034.073l-.006.013c-.013.024-.027.047-.042.07l-.01.014c-.015.023-.032.046-.05.068l-.012.015c-.017.02-.036.04-.055.06l-.015.014a3.5 3.5 0 01-.06.056l-.018.015c-.02.017-.043.034-.065.05l-.022.015c-.024.014-.047.028-.072.042l-.024.014c-.025.012-.05.024-.076.035l-.028.012c-.026.01-.053.02-.08.028l-.03.01c-.027.008-.056.015-.084.02l-.032.008c-.03.005-.06.01-.09.014l-.034.004a5.51 5.51 0 01-.635.037h-.05l-.1-.002h-.033a5.51 5.51 0 01-1.285-.156v6.622a5.5 5.5 0 11-2-4.24v2.54a3.5 3.5 0 101.5 2.9v-9.2s0-1 1-1c1 0 1.25.1 1.25.1a5.5 5.5 0 001.75 3.15V.02h-5.5z" />
    </svg>
  );
}

function pageKeyFromPath(pathname) {
  if (pathname === "/") return "home";
  if (pathname.startsWith("/book")) return "book";
  if (pathname.startsWith("/tours")) return "tours";
  if (pathname.startsWith("/reviews")) return "reviews";
  if (pathname.startsWith("/about")) return "about";
  if (pathname.startsWith("/contact")) return "contact";
  if (pathname.startsWith("/login")) return "login";
  if (pathname.startsWith("/signup")) return "signup";
  if (pathname.startsWith("/account")) return "account";
  if (pathname.startsWith("/bookings")) return "bookings";
  if (pathname.startsWith("/forgot-password")) return "forgot_password";
  if (pathname.startsWith("/reset-password")) return "reset_password";
  return "";
}

function RouteFallback() {
  return (
    <div className="max-w-6xl mx-auto px-4 py-16">
      <div className="h-3 w-36 rounded-full bg-ocean-100 animate-pulse" />
      <div className="mt-4 h-10 w-full max-w-md rounded-xl bg-white border border-ocean-100 animate-pulse" />
    </div>
  );
}

function NavItem({ to, children, preloadKey }) {
  return (
    <NavLink to={to} onMouseEnter={() => preloadRoute(preloadKey)} onFocus={() => preloadRoute(preloadKey)} className={({ isActive }) =>
      `px-3 py-2 rounded-full transition-colors ${isActive ? "bg-ocean-100 text-ocean-900" : "text-ocean-700 hover:text-ocean-900"}`
    }>{children}</NavLink>
  );
}

function MItem({ to, children, onClick, preloadKey }) {
  return (
    <NavLink to={to} onMouseEnter={() => preloadRoute(preloadKey)} onFocus={() => preloadRoute(preloadKey)} onClick={onClick} className={({ isActive }) =>
      `px-4 py-3 rounded-xl transition-colors ${isActive ? "bg-ocean-100 text-ocean-900 font-semibold" : "text-ocean-800 hover:bg-ocean-50"}`
    }>{children}</NavLink>
  );
}
