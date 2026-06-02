import Tours from "../../src/views/Tours.jsx";
import { getSite, getTours, metadataForPath } from "../../src/lib/serverApi.js";

export const dynamic = "force-dynamic";

export async function generateMetadata() {
  return metadataForPath("/tours");
}

export default async function Page() {
  const [site, tours] = await Promise.all([getSite(), getTours()]);
  return <Tours initialSite={site} initialTours={tours} />;
}
