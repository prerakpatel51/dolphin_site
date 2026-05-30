import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const nextConfig = {
  output: "standalone",
  skipTrailingSlashRedirect: true,
  async rewrites() {
    const backend = process.env.BACKEND_UPSTREAM
      ? `http://${process.env.BACKEND_UPSTREAM}`
      : process.env.INTERNAL_API_ORIGIN || process.env.INTERNAL_API_BASE?.replace(/\/api\/?$/, "") || "http://localhost:8000";

    return [
      { source: "/admin", destination: `${backend}/admin/` },
      { source: "/admin/:path*/", destination: `${backend}/admin/:path*/` },
      { source: "/admin/:path*", destination: `${backend}/admin/:path*` },
      { source: "/media/:path*/", destination: `${backend}/media/:path*/` },
      { source: "/media/:path*", destination: `${backend}/media/:path*` },
      { source: "/static/:path*/", destination: `${backend}/static/:path*/` },
      { source: "/static/:path*", destination: `${backend}/static/:path*` },
    ];
  },
  webpack(config) {
    config.resolve.alias["react-router-dom"] = path.resolve(__dirname, "src/lib/router-shim.jsx");
    return config;
  },
};

export default nextConfig;
