import { api } from "../../src/lib/api.js";

test("guest POST requests include the CSRF header from the cookie", async () => {
  document.cookie = "csrftoken=test-csrf-token";
  global.fetch = vi.fn().mockResolvedValue({
    ok: true,
    status: 200,
    json: vi.fn().mockResolvedValue({ ok: true }),
  });

  await api.contact({ name: "A", email: "a@example.com", message: "Hi" });

  expect(global.fetch).toHaveBeenCalledWith(
    "/api/contact/",
    expect.objectContaining({
      method: "POST",
      credentials: "include",
      headers: expect.objectContaining({ "X-CSRFToken": "test-csrf-token" }),
    })
  );
});

test("failed requests surface the backend error detail", async () => {
  global.fetch = vi.fn().mockResolvedValue({
    ok: false,
    status: 400,
    statusText: "Bad Request",
    json: vi.fn().mockResolvedValue({ detail: "Something went wrong" }),
  });

  await expect(api.lookupBookings({ email: "a@example.com", last_name: "Doe" }))
    .rejects.toThrow("Something went wrong");
});
