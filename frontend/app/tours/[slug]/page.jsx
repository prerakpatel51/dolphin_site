import TourDetail from "../../../src/views/TourDetail.jsx";
import { getTour, getTourDates, metadataForPath } from "../../../src/lib/serverApi.js";

export async function generateMetadata({ params }) {
  const { slug } = await params;
  const tour = await getTour(slug);
  if (!tour) return metadataForPath(`/tours/${slug}`, { title: "Tour Not Found | Dolphin Island Tours" });
  return metadataForPath(`/tours/${slug}`, {
    title: tour.seo_title || `${tour.name} | Dolphin Island Tours`,
    description: tour.seo_description || tour.short_description,
    keywords: tour.seo_keywords,
    image: tour.og_image_url || tour.image_url,
    type: "product",
  });
}

export default async function Page({ params }) {
  const { slug } = await params;
  const [tour, dates] = await Promise.all([getTour(slug), getTourDates(slug)]);
  return <TourDetail initialTour={tour} initialDates={dates} />;
}
