import { clearTokens } from "../../src/lib/api.js";

test("logout sends the CSRF header required for cookie auth", async () => {
  document.cookie = "csrftoken=test-csrf-token";
  global.fetch = vi.fn().mockResolvedValue({
    ok: true,
    status: 204,
  });

  await clearTokens();

  expect(global.fetch).toHaveBeenCalledWith("/api/auth/logout/", {
    method: "POST",
    credentials: "include",
    headers: { "X-CSRFToken": "test-csrf-token" },
  });
});

test("logout surfaces request failures instead of pretending it succeeded", async () => {
  document.cookie = "csrftoken=test-csrf-token";
  global.fetch = vi.fn().mockResolvedValue({
    ok: false,
    status: 403,
    statusText: "Forbidden",
    json: vi.fn().mockResolvedValue({ detail: "CSRF Failed" }),
  });

  await expect(clearTokens()).rejects.toThrow("CSRF Failed");
});
