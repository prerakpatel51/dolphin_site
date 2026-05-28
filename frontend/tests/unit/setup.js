import "@testing-library/jest-dom/vitest";

function storageShim() {
  let values = new Map();
  return {
    clear: () => values.clear(),
    getItem: (key) => values.get(String(key)) ?? null,
    key: (index) => Array.from(values.keys())[index] ?? null,
    removeItem: (key) => values.delete(String(key)),
    setItem: (key, value) => values.set(String(key), String(value)),
    get length() {
      return values.size;
    },
  };
}

if (!globalThis.localStorage) {
  globalThis.localStorage = storageShim();
}

if (!globalThis.sessionStorage) {
  globalThis.sessionStorage = storageShim();
}

afterEach(() => {
  document.head.innerHTML = "";
  document.body.innerHTML = "";
  document.cookie.split(";").forEach((cookie) => {
    const name = cookie.split("=")[0]?.trim();
    if (name) {
      document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/`;
    }
  });
  localStorage.clear();
  sessionStorage.clear();
  vi.restoreAllMocks();
});
