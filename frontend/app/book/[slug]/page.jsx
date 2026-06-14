import Book from "../../../src/views/Book.jsx";
import { metadataForPath } from "../../../src/lib/serverApi.js";

export async function generateMetadata({ params }) {
  const { slug } = await params;
  return metadataForPath(`/book/${slug}`, { robots: "noindex, follow" });
}

export default function Page() {
  return <Book />;
}
