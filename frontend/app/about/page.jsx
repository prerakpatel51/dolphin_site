import About from "../../src/views/About.jsx";
import { metadataForPath } from "../../src/lib/serverApi.js";

export async function generateMetadata() {
  return metadataForPath("/about");
}

export default function Page() {
  return <About />;
}
