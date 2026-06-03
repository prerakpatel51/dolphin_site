import { Suspense } from "react";
import "../src/index.css";
import Providers from "./providers.jsx";
import SiteShell from "../src/components/SiteShell.jsx";
import GoogleSiteVerification from "../src/components/GoogleSiteVerification.jsx";

export const viewport = {
  width: "device-width",
  initialScale: 1,
};

export const metadata = {
  verification: {
    google: "N2YGkA7zsA2YGHfr5RFVhDCFnSmQIbn7LI30P6RfEMs",
  },
  other: {
    "google-site-verification": "N2YGkA7zsA2YGHfr5RFVhDCFnSmQIbn7LI30P6RfEMs",
  },
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <link rel="icon" href="/images/logo.png" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link href="https://fonts.googleapis.com/css2?family=Fraunces:wght@500;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
      </head>
      <body className="bg-ocean-50 text-ocean-950 font-sans antialiased">
        <GoogleSiteVerification />
        <Providers>
          <Suspense fallback={null}>
            <SiteShell>{children}</SiteShell>
          </Suspense>
        </Providers>
      </body>
    </html>
  );
}
