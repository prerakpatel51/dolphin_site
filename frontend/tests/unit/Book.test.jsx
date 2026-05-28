import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import Book from "../../src/pages/Book.jsx";
import { api } from "../../src/lib/api.js";

const mockNavigateTarget = "Bookings page";

let mockUser;

vi.mock("../../src/lib/api.js", () => ({
  api: {
    config: vi.fn(),
    slot: vi.fn(),
    validatePromo: vi.fn(),
    createAndPay: vi.fn(),
  },
}));

vi.mock("../../src/lib/auth.jsx", () => ({
  useAuth: () => ({ user: mockUser }),
}));

vi.mock("../../src/lib/site.js", () => ({
  useSite: () => ({
    site: {
      site_name: "Dolphin Island Tours",
      google_analytics_id: "",
      google_ads_id: "",
      meta_pixel_id: "",
    },
  }),
}));

vi.mock("../../src/lib/tracking.js", () => ({
  trackBookingConversion: vi.fn(),
}));

vi.mock("../../src/components/SEO.jsx", () => ({
  default: () => null,
}));

const testTour = {
  id: 1,
  slug: "wildlife",
  name: "Wildlife Tour",
  price_per_person: 60,
  min_party: 2,
  tax_rate_percent: "0.00",
};

const testSlot = {
  id: 101,
  tour: testTour,
  date: "2030-06-15",
  time: "09:00:00",
  seats_remaining: 6,
};

const config = {
  price_per_person: 60,
  fake_payments: true,
};

function renderBook(route = "/book/wildlife?slot=101") {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter
        initialEntries={[route]}
        future={{ v7_relativeSplatPath: true, v7_startTransition: true }}
      >
        <Routes>
          <Route path="/book/:slug" element={<Book />} />
          <Route path="/bookings" element={<div>{mockNavigateTarget}</div>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  );
}

function setPendingBooking(overrides = {}) {
  sessionStorage.setItem("pendingBooking:101", JSON.stringify({
    party_size: 3,
    travelers: [
      { name: "Alex Rider", age: 34 },
      { name: "Sam Rider", age: 31 },
      { name: "Taylor Rider", age: 9 },
    ],
    ...overrides,
  }));
}

beforeEach(() => {
  mockUser = {
    id: 7,
    username: "guest",
    first_name: "Guest",
    last_name: "User",
    email: "guest@example.com",
    phone: "5551234567",
  };
  api.config.mockResolvedValue(config);
  api.slot.mockResolvedValue(testSlot);
  api.validatePromo.mockResolvedValue({
    valid: true,
    code: "SAVE25",
    kind: "percent",
    percent_off: 25,
    discount_cents: 4500,
  });
  api.createAndPay.mockResolvedValue({ id: 321, total_dollars: 135, party_size: 3, slot: testSlot });
});

test("asks anonymous visitors to log in before booking", () => {
  mockUser = null;
  api.config.mockReturnValue(new Promise(() => {}));
  api.slot.mockReturnValue(new Promise(() => {}));

  renderBook();

  expect(screen.getByText("Please log in to book.")).toBeInTheDocument();
  expect(screen.getByRole("link", { name: "Login" })).toHaveAttribute(
    "href",
    "/login?next=/book/wildlife?slot=101"
  );
});

test("shows a blocking state when traveler details are missing", async () => {
  renderBook();

  expect(await screen.findByText("Traveler details are missing.")).toBeInTheDocument();
  expect(screen.getByText("Traveler details were not found.")).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "Pretend to pay $0.00" })).toBeDisabled();
});

test("loads pending traveler details and applies a promo code to the total", async () => {
  const user = userEvent.setup();
  setPendingBooking();

  renderBook();

  expect(await screen.findByRole("heading", { name: "Contact & payment" })).toBeInTheDocument();
  expect(screen.getByText("Alex Rider")).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "Pretend to pay $180.00" })).toBeEnabled();

  await user.type(screen.getByLabelText("Promo code (optional)"), "save25");
  await user.click(screen.getByRole("button", { name: "Apply" }));

  expect(await screen.findByText("SAVE25")).toBeInTheDocument();
  expect(screen.getByText(/saved \$45/)).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "Pretend to pay $135.00" })).toBeEnabled();
  expect(api.validatePromo).toHaveBeenCalledWith({
    code: "SAVE25",
    email: "guest@example.com",
    subtotal_cents: 18000,
  });
});

test("submits the fake-payment booking and clears pending session state", async () => {
  const user = userEvent.setup();
  setPendingBooking();

  renderBook();

  await user.click(await screen.findByRole("button", { name: "Pretend to pay $180.00" }));

  await waitFor(() => expect(api.createAndPay).toHaveBeenCalledWith({
    slot_id: 101,
    party_size: 3,
    travelers: [
      { name: "Alex Rider", age: 34 },
      { name: "Sam Rider", age: 31 },
      { name: "Taylor Rider", age: 9 },
    ],
    customer_name: "Guest User",
    customer_email: "guest@example.com",
    customer_phone: "5551234567",
    special_requests: "",
    source_id: null,
    promo_code: "",
  }));
  expect(sessionStorage.getItem("pendingBooking:101")).toBeNull();
  expect(await screen.findByText(mockNavigateTarget)).toBeInTheDocument();
});
