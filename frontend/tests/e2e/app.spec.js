import { expect, test } from "@playwright/test";

const testUser = {
  id: 1,
  email: "prerakbackup2023@gmail.com",
  username: "guest",
  first_name: "Guest",
  last_name: "User",
  phone: "3215550100",
  accepts_marketing: true,
};

const testTour = {
  id: 1,
  slug: "wildlife",
  name: "Wildlife Tour",
  short_description: "See dolphins and manatees.",
  long_description: "A guided wildlife trip.",
  duration_minutes: 120,
  price_per_person: 60,
  min_party: 2,
  max_party: 6,
  image_url: "/images/welcome.jpg",
  seo_title: "Admin Wildlife SEO",
  seo_description: "Admin wildlife description.",
  seo_keywords: "wildlife,dolphins",
  og_image_url: null,
};

const testSlot = {
  id: 101,
  tour: testTour,
  date: "2030-06-15",
  time: "09:00:00",
  capacity: 6,
  seats_remaining: 6,
  is_active: true,
  notes: "",
};

const sitePayload = {
  site_name: "Dolphin Island Test",
  tagline: "Explore the wonders of the Space Coast.",
  seo_title: "Admin Global SEO",
  seo_description: "Admin global description",
  seo_keywords: "admin,global",
  contact_email: "admin@example.com",
  contact_phone: "555-0000",
  address: "2700 Harbortown Drive, Merritt Island, FL",
  meeting_instructions: "Arrive early.",
  hours: "Open daily",
  maps_url: "",
  map_embed_url: "",
  price_blurb: "$60 per person",
  review_count: 500,
  average_rating: "5.0",
  google_analytics_id: "G-TEST123",
  google_tag_manager_id: "GTM-TEST123",
  google_ads_id: "",
  google_ads_booking_conversion_label: "",
  meta_pixel_id: "",
  facebook_url: "",
  instagram_url: "",
  youtube_url: "",
  tiktok_url: "",
  tripadvisor_url: "",
  google_business_url: "https://www.google.com/maps/search/?api=1&query=Dolphin+Island+Tours+LLC",
  google_review_url: "https://www.google.com/search?q=Dolphin+Island+Tours+LLC+write+a+review",
  google_reviews_url: "https://www.google.com/search?q=Dolphin+Island+Tours+LLC+Google+reviews",
  google_reviews_embed_url: "https://www.google.com/maps?q=Dolphin+Island+Tours+LLC&output=embed",
  images: {
    hero: { key: "hero", image_url: "/images/hero-ocean.jpg", default_path: "/images/hero-ocean.jpg", alt_text: "", caption: "" },
  },
  pages: {
    home: {
      page: "home",
      seo_title: "Admin Home SEO",
      seo_description: "Admin home description",
      seo_keywords: "admin,home",
      hero_title: "Admin managed hero",
      hero_subtitle: "Admin managed subtitle",
      hero_image_url: "/images/hero-ocean.jpg",
      primary_button_label: "Book a tour",
      primary_button_url: "/tours",
      secondary_button_label: "What you'll see",
      secondary_button_url: "#highlights",
      intro_eyebrow: "What you'll see",
      intro_title: "Admin intro",
      section_one_title: "Admin tours",
      section_two_title: "Admin reviews",
      cta_title: "Admin CTA",
      cta_body: "Admin CTA body",
      extra_content: {},
    },
    tours: {
      page: "tours",
      seo_title: "Admin Tours SEO",
      seo_description: "Admin tours description",
      seo_keywords: "admin,tours",
      hero_title: "Tours",
      hero_subtitle: "Small groups.",
      hero_image_url: "/images/sunset-water.jpg",
      extra_content: {},
    },
  },
};

async function mockApi(page) {
  await page.route("**/api/site/", route => route.fulfill({ json: sitePayload }));
  await page.route("**/api/config/", route => route.fulfill({
    json: {
      price_per_person: 60,
      min_party: 2,
      max_party: 6,
      square_app_id: "",
      square_location_id: "",
      square_env: "sandbox",
      fake_payments: true,
    },
  }));
  await page.route("**/api/auth/me/", route => route.fulfill({ status: 401, json: { detail: "Not authenticated" } }));
  await page.route("**/api/tours/wildlife/dates/", route => route.fulfill({
    json: { dates: { "2030-06-15": [{ id: 101, time: "09:00", seats_remaining: 6 }] } },
  }));
  await page.route("**/api/tours/wildlife/", route => route.fulfill({ json: testTour }));
  await page.route("**/api/tours/", route => route.fulfill({ json: [testTour] }));
  await page.route("**/api/slots/101/", route => route.fulfill({ json: testSlot }));
  await page.route("**/api/slots/?tour=wildlife", route => route.fulfill({ json: [testSlot] }));
}

test.beforeEach(async ({ page }) => {
  await mockApi(page);
});

test("checkout promo flow validates code and updates total", async ({ page }) => {
  await page.addInitScript(() => {
    window.sessionStorage.setItem("pendingBooking:101", JSON.stringify({
      party_size: 3,
      travelers: [
        { name: "Guest One", age: "30" },
        { name: "Guest Two", age: "31" },
        { name: "Guest Three", age: "32" },
      ],
    }));
  });
  let bookingBody;
  await page.route("**/api/bookings/create-and-pay/", async route => {
    bookingBody = route.request().postDataJSON();
    await route.fulfill({
      status: 201,
      json: {
        id: "booking-101",
        slot: testSlot,
        party_size: 3,
        price_per_person_cents: 6000,
        tax_cents: 0,
        total_cents: 13500,
        total_dollars: 135,
        discount_cents: 4500,
        promo_code_label: "SAVE25",
        status: "paid",
        customer_name: "Guest Buyer",
        customer_email: "guest@example.com",
        customer_phone: "3215550100",
        travelers: [
          { name: "Guest One", age: 30 },
          { name: "Guest Two", age: 31 },
          { name: "Guest Three", age: 32 },
        ],
        special_requests: "",
        created_at: "2030-06-01T12:00:00Z",
      },
    });
  });
  let promoBody;
  await page.route("**/api/promo/validate/", async route => {
    promoBody = route.request().postDataJSON();
    await route.fulfill({
      json: {
        valid: true,
        code: "SAVE25",
        kind: "percent",
        percent_off: 25,
        amount_off_cents: 0,
        discount_cents: 4500,
        label: "Test promo",
      },
    });
  });

  await page.goto("/book/wildlife?slot=101");
  await expect(page.getByRole("heading", { name: "Contact & payment" })).toBeVisible();
  await page.getByLabel("First name").fill("Guest");
  await page.getByLabel("Last name").fill("Buyer");
  await page.getByLabel("Email").fill("guest@example.com");
  await page.getByLabel("Phone").fill("3215550100");
  await page.getByPlaceholder("E.g. DI1-AB23CD").fill("save25");
  await page.getByRole("button", { name: "Apply" }).click();

  await expect(page.getByText("SAVE25")).toBeVisible();
  await expect(page.getByText(/saved \$45/)).toBeVisible();
  await expect(page.getByRole("button", { name: "Pretend to pay $135" })).toBeEnabled();
  expect(promoBody).toEqual({
    code: "SAVE25",
    email: "guest@example.com",
    subtotal_cents: 18000,
  });
  const [download] = await Promise.all([
    page.waitForEvent("download"),
    page.getByRole("button", { name: "Pretend to pay $135.00" }).click(),
  ]);
  expect(download.suggestedFilename()).toContain("dolphin-island-confirmation-booking-101");
  await expect(page.getByRole("heading", { name: "You are booked." })).toBeVisible();
  await expect(page.getByText("A confirmation email was sent to guest@example.com.")).toBeVisible();
  expect(bookingBody.customer_email).toBe("guest@example.com");
  expect(bookingBody.source_id).toBeNull();
});

test("guest can find booking and download receipt without logging in", async ({ page }) => {
  let lookupBody;
  await page.route("**/api/bookings/lookup/", async route => {
    lookupBody = route.request().postDataJSON();
    await route.fulfill({
      json: {
        results: [{
          id: "booking-101",
          slot: testSlot,
          party_size: 3,
          price_per_person_cents: 6000,
          tax_cents: 0,
          total_cents: 18000,
          total_dollars: 180,
          discount_cents: 0,
          promo_code_label: "",
          status: "paid",
          customer_name: "Guest Buyer",
          customer_email: "guest@example.com",
          customer_phone: "3215550100",
          travelers: [
            { name: "Guest One", age: 30 },
            { name: "Guest Two", age: 31 },
            { name: "Guest Three", age: 32 },
          ],
          special_requests: "",
          created_at: "2030-06-01T12:00:00Z",
        }],
      },
    });
  });

  await page.goto("/find-booking");
  await expect(page.getByRole("heading", { name: "Find your booking" })).toBeVisible();
  await expect(page.getByRole("link", { name: /^Login$/ })).toHaveCount(0);
  await page.getByLabel("Email").fill("guest@example.com");
  await page.getByLabel("Last name").fill("Buyer");
  await page.getByRole("button", { name: "Find booking" }).click();

  await expect(page.getByText("Wildlife Tour")).toBeVisible();
  await expect(page.getByText("Confirmation #booking-101")).toBeVisible();
  await expect(page.getByRole("link", { name: "Download receipt" })).toHaveAttribute(
    "download",
    "dolphin-island-confirmation-booking-101.html"
  );
  expect(lookupBody).toEqual({ email: "guest@example.com", last_name: "Buyer" });
});

test("admin SEO content from site API updates document metadata", async ({ page }) => {
  await page.goto("/");

  await expect(page).toHaveTitle("Admin Home SEO");
  await expect(page.locator('meta[name="description"]')).toHaveAttribute("content", "Admin home description");
  await expect(page.locator('meta[name="keywords"]')).toHaveAttribute("content", "admin,home");
  await expect(page.getByRole("heading", { name: "Admin managed hero" })).toBeVisible();
});

test("key pages do not create horizontal overflow and reviews use Google links", async ({ page }) => {
  await page.addInitScript(() => {
    window.sessionStorage.setItem("pendingBooking:101", JSON.stringify({
      party_size: 3,
      travelers: [
        { name: "Guest One", age: "30" },
        { name: "Guest Two", age: "31" },
        { name: "Guest Three", age: "32" },
      ],
    }));
  });

  for (const viewport of [
    { width: 375, height: 812 },
    { width: 768, height: 1024 },
    { width: 1280, height: 900 },
  ]) {
    await page.setViewportSize(viewport);
    for (const path of ["/", "/tours", "/tours/wildlife", "/book/wildlife?slot=101", "/reviews", "/find-booking"]) {
      await page.goto(path);
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
      expect(overflow, `${path} overflowed at ${viewport.width}px`).toBeLessThanOrEqual(2);
    }
  }

  await page.goto("/reviews#write-review");
  await expect(page.getByRole("heading", { name: "Reviews live on Google." })).toBeVisible();
  await expect(page.getByRole("link", { name: "Add a Google review" })).toHaveAttribute("href", /google\.com/);
  await expect(page.getByText("No Dolphin Island Tours account is required.")).toBeVisible();
  await expect(page.getByRole("button", { name: "Submit review" })).toHaveCount(0);
});
