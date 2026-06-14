import { expect, test } from "@playwright/test";

test.describe.configure({ mode: "serial" });

const stamp = Date.now();
const user = {
  firstName: "Compose",
  lastName: "Browser",
  email: `compose-browser-${stamp}@example.com`,
  phone: "3215550166",
  password: "StrongPass123",
};

const admin = {
  email: process.env.E2E_ADMIN_EMAIL || "admin@example.com",
  password: process.env.E2E_ADMIN_PASSWORD || "StrongPass123!",
};

const adminSmokePaths = [
  "/admin/reports/",
  "/admin/api/activitylog/",
  "/admin/api/booking/",
  "/admin/api/contactmessage/",
  "/admin/api/emailcampaign/",
  "/admin/api/emaildeliveryjob/",
  "/admin/api/emaildeliveryrecipient/",
  "/admin/api/mailinglistentry/",
  "/admin/api/navigationlink/",
  "/admin/api/pagecontent/",
  "/admin/api/promocode/",
  "/admin/api/siteimage/",
  "/admin/api/sitesettings/",
  "/admin/api/tourslot/",
  "/admin/api/tour/",
  "/admin/api/user/",
  "/admin/auth/group/",
];

const monthNames = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
];

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

async function firstBookableSlot(page) {
  const response = await page.request.get("/api/tours/dolphin-wildlife-excursion/dates/");
  expect(response.ok()).toBeTruthy();
  const payload = await response.json();
  for (const [date, slots] of Object.entries(payload.dates || {})) {
    const slot = slots.find((candidate) => candidate.seats_remaining >= 3);
    if (slot) return { date, time: slot.time.slice(0, 5) };
  }
  throw new Error("No dolphin wildlife slots have at least 3 seats remaining.");
}

async function selectCalendarDate(page, isoDate) {
  const target = new Date(`${isoDate}T00:00:00`);
  const today = new Date();
  const monthDiff = (target.getFullYear() - today.getFullYear()) * 12 + target.getMonth() - today.getMonth();
  const direction = monthDiff < 0 ? "Previous month" : "Next month";
  for (let i = 0; i < Math.abs(monthDiff); i += 1) {
    await page.getByLabel(direction).click();
  }
  await expect(page.getByText(`${monthNames[target.getMonth()]} ${target.getFullYear()}`)).toBeVisible();
  await page.getByRole("button", { name: String(target.getDate()), exact: true }).click();
}

test("full local stack supports guest booking, receipt download, Google reviews, and admin", async ({ page }) => {
  test.setTimeout(90_000);
  const consoleErrors = [];
  page.on("console", (message) => {
    if (message.type() === "error") consoleErrors.push(message.text());
  });

  await page.goto("/tours/dolphin-wildlife-excursion");
  await expect(page.getByRole("heading", { name: "Dolphin Wildlife Excursion" })).toBeVisible();
  await expect(page.getByRole("link", { name: /^Login$/ })).toHaveCount(0);
  await expect(page.getByRole("link", { name: /^Sign up$/ })).toHaveCount(0);
  const bookableSlot = await firstBookableSlot(page);
  await selectCalendarDate(page, bookableSlot.date);
  await page.getByRole("button", { name: new RegExp(`^${escapeRegExp(bookableSlot.time)}`) }).click();
  const names = page.getByPlaceholder("Full name");
  const ages = page.getByPlaceholder("Age");
  for (let i = 0; i < 3; i += 1) {
    await names.nth(i).fill(`Guest ${i + 1}`);
    await ages.nth(i).fill(String(30 + i));
  }
  await page.getByRole("button", { name: "Continue to contact & payment" }).click();

  await expect(page).toHaveURL(/\/book\/dolphin-wildlife-excursion\?slot=\d+/, { timeout: 15_000 });
  await expect(page.getByRole("heading", { name: "Contact & payment" })).toBeVisible({ timeout: 15_000 });
  await page.getByLabel("Full name").fill(`${user.firstName} ${user.lastName}`);
  await page.getByLabel("Email").fill(user.email);
  await page.getByLabel("Phone").fill(user.phone);
  await expect(page.getByText("Test mode - fake payment")).toBeVisible();
  const [download] = await Promise.all([
    page.waitForEvent("download"),
    page.getByRole("button", { name: /Pretend to pay/ }).click(),
  ]);
  expect(download.suggestedFilename()).toContain("dolphin-island-confirmation");
  await expect(page.getByRole("heading", { name: "You are booked." })).toBeVisible();
  await expect(page.getByText(`A confirmation email was sent to ${user.email}.`)).toBeVisible();
  await expect(page.getByText("Dolphin Wildlife Excursion").first()).toBeVisible();

  await page.goto("/reviews#write-review");
  await expect(page.getByRole("heading", { name: "Reviews live on Google." })).toBeVisible();
  const addGoogleReview = page.getByRole("link", { name: "Add a Google review" });
  await expect(addGoogleReview).toBeVisible();
  await expect(addGoogleReview).toHaveAttribute("href", /google\.com/);
  await expect(page.getByText("No Dolphin Island Tours account is required.")).toBeVisible();

  await page.goto("/admin/login/");
  await page.locator('input[name="username"]').fill(admin.email);
  await page.locator('input[name="password"]').fill(admin.password);
  await page.locator('input[type="submit"]').click();
  await expect(page.getByText("Operations")).toBeVisible();
  await expect(page.getByText("Financial reports")).toBeVisible();

  for (const path of adminSmokePaths) {
    const response = await page.goto(path);
    expect(response?.ok()).toBeTruthy();
    await expect(page.locator("#content")).toBeVisible();
  }
  const reviewAdminResponse = await page.request.get("/admin/api/review/");
  expect(reviewAdminResponse?.status()).toBe(404);

  await page.goto("/admin/api/booking/");
  await expect(page.getByText(user.email)).toBeVisible();

  const unexpectedConsoleErrors = consoleErrors.filter((text) => (
    !text.includes("favicon")
    && !text.includes("status of 401")
    && !text.includes("Cross-Origin-Opener-Policy header has been ignored")
    && !text.includes("Logout failed TypeError: Failed to fetch")
  ));
  expect(unexpectedConsoleErrors).toEqual([]);
});
