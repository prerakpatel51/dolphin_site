import Contact from "../../src/views/Contact.jsx";
import { metadataForPath } from "../../src/lib/serverApi.js";

export async function generateMetadata() {
  return metadataForPath("/contact");
}

export default function Page() {
  return <Contact />;
}
