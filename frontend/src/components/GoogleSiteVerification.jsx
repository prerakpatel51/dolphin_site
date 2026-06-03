"use client";

import { useServerInsertedHTML } from "next/navigation";

export default function GoogleSiteVerification() {
  useServerInsertedHTML(() => (
    <meta name="google-site-verification" content="N2YGkA7zsA2YGHfr5RFVhDCFnSmQIbn7LI30P6RfEMs" />
  ));

  return null;
}
