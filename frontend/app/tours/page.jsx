import Tours from "../../src/views/Tours.jsx";
import { getTours, metadataForPath } from "../../src/lib/serverApi.js";

export async function generateMetadata() {
  return metadataForPath("/tours");
}

export default async function Page() {
  const tours = await getTours();
  return <Tours initialTours={tours} />;
}
