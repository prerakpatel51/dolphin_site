import Home from "../src/views/Home.jsx";
import { getSite, getTours, metadataForPath } from "../src/lib/serverApi.js";

export const dynamic = "force-dynamic";

export async function generateMetadata() {
  return metadataForPath("/");
}

export default async function Page() {
  const [site, tours] = await Promise.all([
    getSite(),
    getTours(),
  ]);

  return (
    <Home
      initialSite={site}
      initialTours={tours}
    />
  );
}
