function money(cents = 0) {
  return `$${(Number(cents || 0) / 100).toFixed(2)}`;
}

function escapeHtml(value = "") {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

export function bookingDate(booking) {
  return new Date(booking.slot.date + "T00:00:00").toLocaleDateString(undefined, {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

export function confirmationFilename(booking) {
  return `dolphin-island-confirmation-${booking.id}.html`;
}

export function confirmationHtml(booking, site) {
  const tourName = booking.slot.tour?.name || "Dolphin Island Tours";
  const meetingAddress = site?.address || "2700 Harbor Town Drive, Merritt Island, FL 32952";
  const meetingInstructions = site?.meeting_instructions || "Arrive 15 minutes before departure.";
  const travelerRows = (booking.travelers || []).map((traveler, index) => (
    `<li>${escapeHtml(traveler.name || `Guest ${index + 1}`)}${traveler.age !== undefined && traveler.age !== "" ? `, age ${escapeHtml(traveler.age)}` : ""}</li>`
  )).join("");

  return `<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Dolphin Island Tours Confirmation ${escapeHtml(booking.id)}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font-family: Arial, sans-serif; color: #0b3a52; margin: 0; padding: 32px; background: #f4fbfe; }
    .receipt { max-width: 720px; margin: 0 auto; background: white; border: 1px solid #d4edf5; border-radius: 14px; padding: 28px; }
    h1 { margin: 0 0 6px; color: #0b6a8a; }
    .muted { color: #557287; }
    .status { display: inline-block; padding: 5px 10px; border-radius: 999px; background: #dcfce7; color: #166534; font-size: 12px; font-weight: 700; text-transform: uppercase; }
    table { width: 100%; border-collapse: collapse; margin-top: 24px; }
    td { padding: 10px 0; border-bottom: 1px solid #e6f4f8; vertical-align: top; }
    td:first-child { font-weight: 700; width: 38%; }
    .total { font-size: 24px; font-weight: 800; color: #08384d; }
    .travelers { margin-top: 24px; padding: 18px; background: #f4fbfe; border: 1px solid #d4edf5; border-radius: 12px; }
    .travelers h2 { margin: 0 0 10px; font-size: 18px; }
    .travelers ol { margin: 0; padding-left: 22px; }
    .travelers li { margin: 5px 0; }
    .footer { margin-top: 24px; font-size: 13px; color: #557287; line-height: 1.5; }
    @media print { body { background: white; padding: 0; } .receipt { border: 0; } }
  </style>
</head>
<body>
  <main class="receipt">
    <h1>Dolphin Island Tours</h1>
    <p class="muted">Booking confirmation and receipt</p>
    <p><span class="status">${escapeHtml(booking.status)}</span></p>
    <table>
      <tr><td>Confirmation #</td><td>${escapeHtml(booking.id)}</td></tr>
      <tr><td>Tour</td><td>${escapeHtml(tourName)}</td></tr>
      <tr><td>Date</td><td>${escapeHtml(bookingDate(booking))}</td></tr>
      <tr><td>Time</td><td>${escapeHtml(booking.slot.time.slice(0, 5))}</td></tr>
      <tr><td>Guests</td><td>${escapeHtml(booking.party_size)}</td></tr>
      <tr><td>Name</td><td>${escapeHtml(booking.customer_name)}</td></tr>
      <tr><td>Email</td><td>${escapeHtml(booking.customer_email)}</td></tr>
      <tr><td>Phone</td><td>${escapeHtml(booking.customer_phone || "N/A")}</td></tr>
      <tr><td>Price per person</td><td>${money(booking.price_per_person_cents)}</td></tr>
      ${booking.discount_cents ? `<tr><td>Discount</td><td>-${money(booking.discount_cents)}${booking.promo_code_label ? ` (${escapeHtml(booking.promo_code_label)})` : ""}</td></tr>` : ""}
      <tr><td>Tax</td><td>${money(booking.tax_cents)}</td></tr>
      <tr><td>Total paid</td><td class="total">${money(booking.total_cents)}</td></tr>
      ${booking.special_requests ? `<tr><td>Special requests</td><td>${escapeHtml(booking.special_requests)}</td></tr>` : ""}
    </table>
    ${travelerRows ? `<section class="travelers"><h2>Travelers</h2><ol>${travelerRows}</ol></section>` : ""}
    <div class="footer">
      <p><b>Meeting point:</b> ${escapeHtml(meetingAddress)}</p>
      <p>${escapeHtml(meetingInstructions)} Bring sunscreen, water, sunglasses, and a camera.</p>
      <p>Generated on ${escapeHtml(new Date().toLocaleString())}</p>
    </div>
  </main>
</body>
</html>`;
}

export function confirmationDataUrl(booking, site) {
  return `data:text/html;charset=utf-8,${encodeURIComponent(confirmationHtml(booking, site))}`;
}

export function downloadBookingConfirmation(booking, site) {
  if (typeof window !== "undefined" && window.navigator?.userAgent?.includes("jsdom")) return;
  const blob = new Blob([confirmationHtml(booking, site)], { type: "text/html;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = confirmationFilename(booking);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}
