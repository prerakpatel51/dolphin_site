import TourDetail from "../../../src/views/TourDetail.jsx";
import { getTour, getTourDates, getSite, metadataForPath } from "../../../src/lib/serverApi.js";
import { tourJsonLd, jsonLdScript } from "../../../src/lib/jsonld.js";

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
  const [tour, dates, site] = await Promise.all([getTour(slug), getTourDates(slug), getSite()]);
  const ld = tour ? tourJsonLd(tour, site) : null;
  return (
    <>
      {ld && (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: jsonLdScript(ld) }}
        />
      )}
      <TourDetail initialTour={tour} initialDates={dates} />
    </>
  );
}
