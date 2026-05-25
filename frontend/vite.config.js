import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: { "/api": "http://localhost:8000" },
  },
  test: {
    environment: "jsdom",
    environmentOptions: {
      jsdom: {
        url: "http://localhost:5173/",
      },
    },
    include: ["tests/unit/**/*.{test,spec}.{js,jsx}"],
    setupFiles: "./tests/unit/setup.js",
    globals: true,
  },
});
