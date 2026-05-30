import ReviewsPage from "../../src/views/ReviewsPage.jsx";
import { metadataForPath } from "../../src/lib/serverApi.js";

export async function generateMetadata() {
  return metadataForPath("/reviews");
}

export default function Page() {
  return <ReviewsPage />;
}
