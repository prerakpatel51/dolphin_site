const HOP_BY_HOP_HEADERS = new Set([
  "connection",
  "content-encoding",
  "content-length",
  "keep-alive",
  "proxy-authenticate",
  "proxy-authorization",
  "te",
  "trailer",
  "transfer-encoding",
  "upgrade",
]);

export const dynamic = "force-dynamic";

function backendOrigin() {
  if (process.env.BACKEND_UPSTREAM) return `http://${process.env.BACKEND_UPSTREAM}`;
  return process.env.INTERNAL_API_ORIGIN
    || process.env.INTERNAL_API_BASE?.replace(/\/api\/?$/, "")
    || "http://localhost:8000";
}

function cleanHeaders(upstream) {
  const headers = new Headers();
  upstream.headers.forEach((value, key) => {
    if (!HOP_BY_HOP_HEADERS.has(key.toLowerCase())) headers.append(key, value);
  });
  return headers;
}

async function fetchRobots() {
  return fetch(`${backendOrigin()}/api/robots.txt`, { cache: "no-store" });
}

export async function GET() {
  const upstream = await fetchRobots();
  return new Response(upstream.body, {
    status: upstream.status,
    statusText: upstream.statusText,
    headers: cleanHeaders(upstream),
  });
}

export async function HEAD() {
  const upstream = await fetchRobots();
  return new Response(null, {
    status: upstream.status,
    statusText: upstream.statusText,
    headers: cleanHeaders(upstream),
  });
}
