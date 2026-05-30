import Home from "../src/views/Home.jsx";
import { getAllReviewStats, getReviews, getSite, getTours, metadataForPath } from "../src/lib/serverApi.js";

export async function generateMetadata() {
  return metadataForPath("/");
}

export default async function Page() {
  const [site, tours, featuredReviews, backupReviews, reviewStats] = await Promise.all([
    getSite(),
    getTours(),
    getReviews({ featured: 1 }),
    getReviews({ sort: "highest" }),
    getAllReviewStats(),
  ]);

  return (
    <Home
      initialSite={site}
      initialTours={tours}
      initialFeaturedReviews={featuredReviews}
      initialBackupReviews={backupReviews}
      initialReviewStats={reviewStats}
    />
  );
}
