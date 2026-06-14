import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import FindBooking from "../../src/views/FindBooking.jsx";
import { api } from "../../src/lib/api.js";

vi.mock("../../src/lib/api.js", () => ({
  api: {
    lookupBookings: vi.fn(),
  },
}));

vi.mock("../../src/lib/site.js", () => ({
  useSite: () => ({
    site: {
      site_name: "Dolphin Island Tours",
      address: "2700 Harbor Town Drive",
      meeting_instructions: "Arrive 15 minutes early.",
    },
    page: {
      seo_title: "Find My Booking | Dolphin Island Tours",
      seo_description: "Find your booking.",
      seo_keywords: "find,booking",
    },
  }),
}));

vi.mock("../../src/components/SEO.jsx", () => ({
  default: () => null,
}));

const booking = {
  id: "booking-123",
  slot: {
    date: "2030-06-15",
    time: "09:00:00",
    tour: { name: "Wildlife Tour" },
  },
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
};

function renderFindBooking() {
  return render(
    <MemoryRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
      <FindBooking />
    </MemoryRouter>
  );
}

test("looks up a booking by email and last name and exposes receipt download", async () => {
  const user = userEvent.setup();
  api.lookupBookings.mockResolvedValue({ results: [booking] });

  renderFindBooking();

  await user.type(screen.getByLabelText("Email"), "guest@example.com");
  await user.type(screen.getByLabelText("Last name"), "Buyer");
  await user.click(screen.getByRole("button", { name: "Find booking" }));

  expect(await screen.findByText("Wildlife Tour")).toBeInTheDocument();
  expect(screen.getByText("Confirmation #booking-123")).toBeInTheDocument();
  expect(screen.getByRole("link", { name: "Download receipt" })).toHaveAttribute(
    "download",
    "dolphin-island-confirmation-booking-123.html"
  );
  expect(api.lookupBookings).toHaveBeenCalledWith({
    email: "guest@example.com",
    last_name: "Buyer",
  });
});

test("shows a no-match state", async () => {
  const user = userEvent.setup();
  api.lookupBookings.mockResolvedValue({ results: [] });

  renderFindBooking();

  await user.type(screen.getByLabelText("Email"), "guest@example.com");
  await user.type(screen.getByLabelText("Last name"), "Other");
  await user.click(screen.getByRole("button", { name: "Find booking" }));

  expect(await screen.findByText(/No booking matched/)).toBeInTheDocument();
});
