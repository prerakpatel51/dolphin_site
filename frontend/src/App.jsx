import { Routes, Route, Link, NavLink, useLocation, useNavigate } from "react-router-dom";
import { Suspense, lazy, useEffect, useState } from "react";
import { useAuth } from "./lib/auth.jsx";
import { useSite } from "./lib/site.js";
import { initMarketingTags, trackPageView } from "./lib/tracking.js";

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
  const [open, setOpen] = useState(false);
  useEffect(() => { initMarketingTags(site); }, [site]);
  useEffect(() => {
    trackPageView(site, `${location.pathname}${location.search}`);
  }, [site, location.pathname, location.search]);
  useEffect(() => { setOpen(false); }, [location.pathname]);

  return (
    <div className="min-h-screen flex flex-col bg-ocean-50 text-ocean-950">
      <header className="sticky top-0 z-40 backdrop-blur-xl bg-white/90 border-b border-ocean-100/80 shadow-sm shadow-ocean-900/5">
        <div className="max-w-6xl mx-auto px-4 h-16 sm:h-[72px] flex items-center justify-between">
          <Link to="/" onClick={() => setOpen(false)} className="flex items-center gap-2 sm:gap-3 min-w-0">
            <img src="/images/logo.png" alt="Dolphin Island Tours" className="h-9 sm:h-10 w-auto" />
            <span className="hidden sm:block font-display text-base sm:text-lg text-ocean-800 truncate">Dolphin Island Tours</span>
          </Link>
          {/* desktop nav */}
          <nav className="hidden md:flex items-center gap-1 lg:gap-3 text-sm">
            <NavItem to="/tours" preloadKey="tours">Tours</NavItem>
            <NavItem to="/about" preloadKey="about">About</NavItem>
            <NavItem to="/contact" preloadKey="contact">Contact</NavItem>
            {user ? (
              <>
                <NavItem to="/bookings" preloadKey="bookings">My Bookings</NavItem>
                <NavItem to="/account" preloadKey="account">Account</NavItem>
                <button onClick={() => { logout(); nav("/"); }} className="text-ocean-700 hover:text-ocean-900 px-2">Logout</button>
              </>
            ) : (
              <>
                <NavItem to="/login" preloadKey="login">Login</NavItem>
                <Link to="/signup" onMouseEnter={() => preloadRoute("signup")} onFocus={() => preloadRoute("signup")} className="btn-primary !py-2 !px-4 text-sm">Sign up</Link>
              </>
            )}
          </nav>
          {/* mobile hamburger */}
          <button onClick={() => setOpen(o => !o)} aria-label="Menu"
            className="md:hidden w-10 h-10 rounded-full hover:bg-ocean-100 flex items-center justify-center">
            <span className="relative w-5 h-4">
              <span className={`absolute left-0 right-0 h-0.5 bg-ocean-800 transition-transform ${open ? "top-1.5 rotate-45" : "top-0"}`} />
              <span className={`absolute left-0 right-0 h-0.5 bg-ocean-800 top-1.5 transition-opacity ${open ? "opacity-0" : "opacity-100"}`} />
              <span className={`absolute left-0 right-0 h-0.5 bg-ocean-800 transition-transform ${open ? "top-1.5 -rotate-45" : "top-3"}`} />
            </span>
          </button>
        </div>
        {/* mobile drawer */}
        {open && (
          <div className="md:hidden border-t border-ocean-100 bg-white shadow-2xl shadow-ocean-950/10">
            <nav className="px-4 py-4 flex flex-col gap-1 text-base">
              <MItem to="/tours" preloadKey="tours" onClick={() => setOpen(false)}>Tours</MItem>
              <MItem to="/about" preloadKey="about" onClick={() => setOpen(false)}>About</MItem>
              <MItem to="/contact" preloadKey="contact" onClick={() => setOpen(false)}>Contact</MItem>
              {user ? (
                <>
                  <MItem to="/bookings" preloadKey="bookings" onClick={() => setOpen(false)}>My Bookings</MItem>
                  <MItem to="/account" preloadKey="account" onClick={() => setOpen(false)}>Account</MItem>
                  <button onClick={() => { setOpen(false); logout(); nav("/"); }}
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
        <Suspense fallback={<RouteFallback />}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/tours" element={<Tours />} />
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
              <img src="/images/logo.png" alt="" className="h-10 sm:h-12 w-auto" />
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
          </div>
        </div>
        <div className="text-center text-xs text-ocean-300 py-4 border-t border-ocean-800">
          &copy; {new Date().getFullYear()} Dolphin Island Tours
        </div>
      </footer>
    </div>
  );
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
