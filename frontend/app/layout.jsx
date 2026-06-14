import { Suspense } from "react";
import "../src/index.css";
import Providers from "./providers.jsx";
import SiteShell from "../src/components/SiteShell.jsx";
import { getSite } from "../src/lib/serverApi.js";
import { localBusinessJsonLd, websiteJsonLd, jsonLdScript } from "../src/lib/jsonld.js";

export const viewport = {
  width: "device-width",
  initialScale: 1,
};

export const metadata = {
  verification: {
    google: "N2YGkA7zsA2YGHfr5RFVhDCFnSmQIbn7LI30P6RfEMs",
  },
};

export default async function RootLayout({ children }) {
  const site = await getSite();
  const logoUrl = site.images?.logo?.image_url || "/images/logo.png";
  const structuredData = [localBusinessJsonLd(site, logoUrl), websiteJsonLd(site)];

  return (
    <html lang="en">
      <head>
        <link rel="icon" href="/images/logo.png" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link href="https://fonts.googleapis.com/css2?family=Fraunces:wght@500;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
        {structuredData.map((data, i) => (
          <script
            key={i}
            type="application/ld+json"
            dangerouslySetInnerHTML={{ __html: jsonLdScript(data) }}
          />
        ))}
      </head>
      <body className="bg-ocean-50 text-ocean-950 font-sans antialiased">
        <Providers>
          <Suspense fallback={null}>
            <SiteShell>{children}</SiteShell>
          </Suspense>
        </Providers>
      </body>
    </html>
  );
}
