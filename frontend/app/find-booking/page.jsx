import FindBooking from "../../src/views/FindBooking.jsx";
import { metadataForPath } from "../../src/lib/serverApi.js";

export async function generateMetadata() {
  return metadataForPath("/find-booking", { robots: "noindex, follow" });
}

export default function Page() {
  return <FindBooking />;
}
