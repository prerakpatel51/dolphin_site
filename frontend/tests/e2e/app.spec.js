import { expect, test } from "@playwright/test";

const testUser = {
  id: 1,
  email: "prerakbackup2023@gmail.com",
  username: "guest",
  first_name: "Guest",
  last_name: "User",
  phone: "555-0100",
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
  google_business_url: "",
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
  await page.route("**/api/auth/me/", route => route.fulfill({ json: testUser }));
  await page.route("**/api/tours/wildlife/dates/", route => route.fulfill({
    json: { dates: { "2030-06-15": [{ id: 101, time: "09:00", seats_remaining: 6 }] } },
  }));
  await page.route("**/api/tours/wildlife/", route => route.fulfill({ json: testTour }));
  await page.route("**/api/tours/wildlife/reviews/stats/", route => route.fulfill({
    json: { count: 0, average: 0, breakdown: {} },
  }));
  await page.route("**/api/tours/", route => route.fulfill({ json: [testTour] }));
  await page.route("**/api/slots/?tour=wildlife", route => route.fulfill({ json: [testSlot] }));
  await page.route("**/api/reviews/**", route => route.fulfill({ json: [] }));
}

test.beforeEach(async ({ page }) => {
  await mockApi(page);
});

test("forgot password sends request and shows inbox success state", async ({ page }) => {
  let requestBody;
  await page.route("**/api/auth/password-reset/", async route => {
    requestBody = route.request().postDataJSON();
    await route.fulfill({ json: { ok: true } });
  });

  await page.goto("/forgot-password");
  await page.locator('input[type="email"]').fill("prerakbackup2023@gmail.com");
  await page.getByRole("button", { name: "Send reset link" }).click();

  await expect(page.getByText("Check your inbox.")).toBeVisible();
  await expect(page.getByText("It expires in 24 hours.")).toBeVisible();
  expect(requestBody).toEqual({ email: "prerakbackup2023@gmail.com" });
});

test("reset password validates locally, submits token, and redirects to login", async ({ page }) => {
  let confirmBody;
  await page.route("**/api/auth/password-reset-confirm/", async route => {
    confirmBody = route.request().postDataJSON();
    await route.fulfill({ json: { ok: true } });
  });

  await page.goto("/reset-password?uid=abc123&token=token123");
  const passwords = page.locator('input[type="password"]');
  await passwords.nth(0).fill("short");
  await passwords.nth(1).fill("short");
  await page.getByRole("button", { name: "Update password" }).click();
  await expect(passwords.nth(0)).toHaveAttribute("minlength", "8");
  expect(await passwords.nth(0).evaluate(el => el.validity.tooShort)).toBe(true);

  await passwords.nth(0).fill("NewStrongPass123");
  await passwords.nth(1).fill("DifferentPass123");
  await page.getByRole("button", { name: "Update password" }).click();
  await expect(page.getByText("Passwords don't match.")).toBeVisible();

  await passwords.nth(1).fill("NewStrongPass123");
  await page.getByRole("button", { name: "Update password" }).click();

  await expect(page.getByText("Password updated.")).toBeVisible();
  await expect(page).toHaveURL(/\/login$/);
  expect(confirmBody).toEqual({ uid: "abc123", token: "token123", password: "NewStrongPass123" });
});

test("checkout promo flow validates code and updates total", async ({ page }) => {
  await page.addInitScript(() => {
    window.localStorage.setItem("auth", JSON.stringify({ access: "test-token", refresh: "refresh-token" }));
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
  await expect(page.getByRole("heading", { name: "Book your tour" })).toBeVisible();
  await page.getByPlaceholder("E.g. DI1-AB23CD").fill("save25");
  await page.getByRole("button", { name: "Apply" }).click();

  await expect(page.getByText("SAVE25")).toBeVisible();
  await expect(page.getByText(/saved \$45/)).toBeVisible();
  await expect(page.getByRole("button", { name: "Pretend to pay $135" })).toBeEnabled();
  expect(promoBody).toEqual({
    code: "SAVE25",
    email: "prerakbackup2023@gmail.com",
    subtotal_cents: 18000,
  });
});

test("admin SEO content from site API updates document metadata", async ({ page }) => {
  await page.goto("/");

  await expect(page).toHaveTitle("Admin Home SEO");
  await expect(page.locator('meta[name="description"]')).toHaveAttribute("content", "Admin home description");
  await expect(page.locator('meta[name="keywords"]')).toHaveAttribute("content", "admin,home");
  await expect(page.getByRole("heading", { name: "Admin managed hero" })).toBeVisible();
});

test("key pages do not create horizontal overflow and review fields are capped", async ({ page }) => {
  await page.addInitScript(() => {
    window.localStorage.setItem("auth", JSON.stringify({ access: "test-token", refresh: "refresh-token" }));
  });

  for (const viewport of [
    { width: 375, height: 812 },
    { width: 768, height: 1024 },
    { width: 1280, height: 900 },
  ]) {
    await page.setViewportSize(viewport);
    for (const path of ["/", "/tours", "/tours/wildlife", "/book/wildlife?slot=101", "/forgot-password", "/reset-password?uid=abc123&token=token123"]) {
      await page.goto(path);
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
      expect(overflow, `${path} overflowed at ${viewport.width}px`).toBeLessThanOrEqual(2);
    }
  }

  await page.goto("/tours/wildlife");
  await expect(page.locator('input[maxlength="80"]')).toHaveCount(1);
  await expect(page.locator('textarea[maxlength="1000"]')).toHaveCount(1);
  await page.locator('textarea[maxlength="1000"]').fill("x".repeat(1200));
  await expect(page.locator('textarea[maxlength="1000"]')).toHaveValue("x".repeat(1000));
});
