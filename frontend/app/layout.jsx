import Script from "next/script";
import { Suspense } from "react";
import "../src/index.css";
import Providers from "./providers.jsx";
import SiteShell from "../src/components/SiteShell.jsx";

export const viewport = {
  width: "device-width",
  initialScale: 1,
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
        <Script src="https://sandbox.web.squarecdn.com/v1/square.js" strategy="afterInteractive" />
        <Providers>
          <Suspense fallback={null}>
            <SiteShell>{children}</SiteShell>
          </Suspense>
        </Providers>
      </body>
    </html>
  );
}
