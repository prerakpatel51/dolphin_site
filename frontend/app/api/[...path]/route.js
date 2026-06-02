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

const METHODS_WITH_BODY = new Set(["POST", "PUT", "PATCH", "DELETE"]);

export const dynamic = "force-dynamic";

function backendOrigin() {
  if (process.env.BACKEND_UPSTREAM) return `http://${process.env.BACKEND_UPSTREAM}`;
  return process.env.INTERNAL_API_ORIGIN
    || process.env.INTERNAL_API_BASE?.replace(/\/api\/?$/, "")
    || "http://localhost:8000";
}

function targetUrl(request, pathParts) {
  const pathname = request.nextUrl.pathname;
  const trailingSlash = pathname.endsWith("/") ? "/" : "";
  const path = pathParts.join("/");
  return `${backendOrigin()}/api/${path}${trailingSlash}${request.nextUrl.search}`;
}

function requestHeaders(request) {
  const headers = new Headers(request.headers);
  const publicHost = request.headers.get("host") || "";
  const publicOrigin = `${request.nextUrl.protocol}//${publicHost}`;
  if (publicHost) headers.set("host", publicHost);
  headers.set("origin", publicOrigin);
  headers.set("referer", `${publicOrigin}/`);
  headers.set("x-forwarded-host", publicHost);
  headers.set("x-forwarded-proto", request.nextUrl.protocol.replace(":", ""));
  for (const header of HOP_BY_HOP_HEADERS) headers.delete(header);
  return headers;
}

function responseHeaders(upstream, request) {
  const headers = new Headers();
  upstream.headers.forEach((value, key) => {
    const k = key.toLowerCase();
    if (!HOP_BY_HOP_HEADERS.has(k) && k !== "set-cookie" && !k.startsWith("access-control-")) {
      headers.append(key, value);
    }
  });

  const isLocalHttp = request.nextUrl.protocol === "http:";
  upstream.headers.getSetCookie?.().forEach((cookie) => {
    headers.append("set-cookie", isLocalHttp ? cookie.replace(/;\s*Secure/gi, "") : cookie);
  });
  return headers;
}

async function proxy(request, context) {
  const { path = [] } = await context.params;
  const hasBody = METHODS_WITH_BODY.has(request.method);
  const body = hasBody ? await request.arrayBuffer() : undefined;
  const upstream = await fetch(targetUrl(request, path), {
    method: request.method,
    headers: requestHeaders(request),
    body,
    redirect: "manual",
  });

  return new Response(upstream.body, {
    status: upstream.status,
    statusText: upstream.statusText,
    headers: responseHeaders(upstream, request),
  });
}

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
export const OPTIONS = proxy;
