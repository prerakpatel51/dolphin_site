import { Routes, Route, Link, NavLink, useLocation, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { useAuth } from "./lib/auth.jsx";
import { useSite } from "./lib/site.js";
import { initMarketingTags, trackPageView } from "./lib/tracking.js";
import Home from "./pages/Home.jsx";
import Tours from "./pages/Tours.jsx";
import TourDetail from "./pages/TourDetail.jsx";
import Book from "./pages/Book.jsx";
import Login from "./pages/Login.jsx";
import Signup from "./pages/Signup.jsx";
import Account from "./pages/Account.jsx";
import MyBookings from "./pages/MyBookings.jsx";
import About from "./pages/About.jsx";
import Contact from "./pages/Contact.jsx";
import ForgotPassword from "./pages/ForgotPassword.jsx";
import ResetPassword from "./pages/ResetPassword.jsx";

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

  return (
    <div className="min-h-screen flex flex-col">
      <header className="sticky top-0 z-40 backdrop-blur bg-white/85 border-b border-ocean-100">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          <Link to="/" onClick={() => setOpen(false)} className="flex items-center gap-2 sm:gap-3 min-w-0">
            <img src="/images/logo.png" alt="Dolphin Island Tours" className="h-9 sm:h-10 w-auto" />
            <span className="hidden sm:block font-display text-base sm:text-lg text-ocean-800 truncate">Dolphin Island Tours</span>
          </Link>
          {/* desktop nav */}
          <nav className="hidden md:flex items-center gap-1 lg:gap-3 text-sm">
            <NavItem to="/tours">Tours</NavItem>
            <NavItem to="/about">About</NavItem>
            <NavItem to="/contact">Contact</NavItem>
            {user ? (
              <>
                <NavItem to="/bookings">My Bookings</NavItem>
                <NavItem to="/account">Account</NavItem>
                <button onClick={() => { logout(); nav("/"); }} className="text-ocean-700 hover:text-ocean-900 px-2">Logout</button>
              </>
            ) : (
              <>
                <NavItem to="/login">Login</NavItem>
                <Link to="/signup" className="btn-primary !py-2 !px-4 text-sm">Sign up</Link>
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
          <div className="md:hidden border-t border-ocean-100 bg-white">
            <nav className="px-4 py-4 flex flex-col gap-1 text-base">
              <MItem to="/tours" onClick={() => setOpen(false)}>Tours</MItem>
              <MItem to="/about" onClick={() => setOpen(false)}>About</MItem>
              <MItem to="/contact" onClick={() => setOpen(false)}>Contact</MItem>
              {user ? (
                <>
                  <MItem to="/bookings" onClick={() => setOpen(false)}>My Bookings</MItem>
                  <MItem to="/account" onClick={() => setOpen(false)}>Account</MItem>
                  <button onClick={() => { setOpen(false); logout(); nav("/"); }}
                    className="text-left px-4 py-3 rounded-xl text-ocean-700 hover:bg-ocean-50">Logout</button>
                </>
              ) : (
                <>
                  <MItem to="/login" onClick={() => setOpen(false)}>Login</MItem>
                  <Link to="/signup" onClick={() => setOpen(false)} className="btn-primary mt-2 text-base">Sign up</Link>
                </>
              )}
            </nav>
          </div>
        )}
      </header>

      <main className="flex-1">
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
        </Routes>
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

function NavItem({ to, children }) {
  return (
    <NavLink to={to} className={({ isActive }) =>
      `px-3 py-2 rounded-full transition-colors ${isActive ? "bg-ocean-100 text-ocean-900" : "text-ocean-700 hover:text-ocean-900"}`
    }>{children}</NavLink>
  );
}

function MItem({ to, children, onClick }) {
  return (
    <NavLink to={to} onClick={onClick} className={({ isActive }) =>
      `px-4 py-3 rounded-xl transition-colors ${isActive ? "bg-ocean-100 text-ocean-900 font-semibold" : "text-ocean-800 hover:bg-ocean-50"}`
    }>{children}</NavLink>
  );
}
