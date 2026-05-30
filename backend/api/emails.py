import smtplib
import ssl
from email.message import EmailMessage
import requests
from django.conf import settings
from django.core import signing
from django.utils.html import escape, linebreaks


UNSUBSCRIBE_PLACEHOLDER = "{{ unsubscribe_url }}"
BUSINESS_ADDRESS = "Dolphin Island Tours, 2700 Harbortown Drive, Merritt Island, FL"


def unsubscribe_token(email):
    return signing.dumps({"email": email.lower()}, salt="marketing-unsubscribe")


def unsubscribe_url_for_email(email):
    base = settings.FRONTEND_URL.rstrip("/")
    return f"{base}/api/unsubscribe/{unsubscribe_token(email)}/"


def add_unsubscribe_url(html, email):
    return html.replace(UNSUBSCRIBE_PLACEHOLDER, escape(unsubscribe_url_for_email(email)))


def user_email_footer(email):
    unsubscribe_url = escape(unsubscribe_url_for_email(email))
    return f"""
    <hr style="border:none;border-top:1px solid #dbeafe;margin:24px 0">
    <p style="color:#64748b;font-size:12px;line-height:1.45">
      Sent by {BUSINESS_ADDRESS}.<br>
      <a href="{unsubscribe_url}" style="color:#1389b1;text-decoration:none">Unsubscribe from marketing emails</a>.
      Booking receipts, password resets, and direct replies may still be sent when needed.
    </p>
    """


def prepare_user_email_html(html, email):
    rendered = add_unsubscribe_url(html, email)
    if UNSUBSCRIBE_PLACEHOLDER in html:
        return rendered
    closing_div = rendered.rfind("</div>")
    if closing_div == -1:
        return rendered + user_email_footer(email)
    return rendered[:closing_div] + user_email_footer(email) + rendered[closing_div:]


def unsubscribe_headers(email):
    unsubscribe_url = unsubscribe_url_for_email(email)
    return {
        "List-Unsubscribe": f"<{unsubscribe_url}>",
        "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
    }


def _send_via_smtp(to, subject, html, headers=None):
    recipients = [to] if isinstance(to, str) else list(to)
    msg = EmailMessage()
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject
    for name, value in (headers or {}).items():
        msg[name] = value
    msg.set_content("This email requires an HTML-capable client.")
    msg.add_alternative(html, subtype="html")
    ctx = ssl.create_default_context()
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=settings.SMTP_TIMEOUT) as s:
        s.ehlo()
        s.starttls(context=ctx)
        s.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        s.send_message(msg)
    return {"id": "smtp-sent", "to": recipients}


def send_email(to, subject, html, include_unsubscribe=True):
    """Send via Gmail SMTP if configured, else Resend, else noop."""
    recipients = [to] if isinstance(to, str) else list(to)
    headers = {}
    if include_unsubscribe and len(recipients) == 1:
        html = prepare_user_email_html(html, recipients[0])
        headers = unsubscribe_headers(recipients[0])
    if getattr(settings, "SMTP_HOST", "") and getattr(settings, "SMTP_USER", ""):
        return _send_via_smtp(to, subject, html, headers=headers)
    if not settings.RESEND_API_KEY:
        return None
    payload = {"from": settings.EMAIL_FROM, "to": recipients, "subject": subject, "html": html}
    if headers:
        payload["headers"] = headers
    r = requests.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {settings.RESEND_API_KEY}", "Content-Type": "application/json"},
        json=payload,
        timeout=15,
    )
    r.raise_for_status()
    return r.json()


def booking_receipt_html(booking):
    customer_name = escape(booking.customer_name)
    booking_id = escape(str(booking.id))
    slot_date = escape(str(booking.slot.date))
    slot_time = escape(str(booking.slot.time))
    travelers = ""
    if booking.travelers:
        rows = "".join(
            f"<li>{escape(str(t.get('name', '')))} - age {escape(str(t.get('age', '')))}</li>"
            for t in booking.travelers
        )
        travelers = f"<p><b>Travelers:</b></p><ol>{rows}</ol>"
    return f"""
    <div style="font-family:system-ui,sans-serif;max-width:560px;margin:0 auto;color:#0b3a52">
      <h2 style="color:#0b6a8a">Booking Confirmed</h2>
      <p>Hi {customer_name}, thanks for booking with Dolphin Island Tours!</p>
      <table style="border-collapse:collapse;width:100%;margin:16px 0">
        <tr><td><b>Confirmation #</b></td><td>{booking_id}</td></tr>
        <tr><td><b>Date</b></td><td>{slot_date}</td></tr>
        <tr><td><b>Time</b></td><td>{slot_time}</td></tr>
        <tr><td><b>Party</b></td><td>{booking.party_size} guests</td></tr>
        <tr><td><b>Tax</b></td><td>${booking.tax_cents/100:.2f}</td></tr>
        <tr><td><b>Total paid</b></td><td>${booking.total_cents/100:.2f}</td></tr>
      </table>
      {travelers}
      <p><b>Meeting point:</b> 2700 Harbortown Drive, Merritt Island, FL</p>
      <p>What to bring: sunscreen, water, sunglasses, camera.</p>
      <p>Questions? Reply to this email or contact lewis@dolphinislandtours.com.</p>
    </div>
    """


def contact_admin_html(msg):
    phone = f" - {escape(msg.phone)}" if msg.phone else ""
    subject = escape(msg.subject or "(none)")
    message = linebreaks(escape(msg.message))
    return f"""
    <h3>New contact inquiry</h3>
    <p><b>{escape(msg.name)}</b> &lt;{escape(msg.email)}&gt;{phone}</p>
    <p><b>Subject:</b> {subject}</p>
    <blockquote style="border-left:3px solid #1389b1;padding-left:12px;color:#0b3a52">{message}</blockquote>
    """


def review_moderation_admin_html(review):
    tour_name = escape(str(review.tour or "General review"))
    title = escape(review.title or "(no title)")
    body = linebreaks(escape(review.body))
    status = "approved automatically" if review.is_approved else "awaiting moderation"
    return f"""
    <h3>New tour review</h3>
    <p><b>{escape(review.author_name)}</b> left a {review.rating}-star review for <b>{tour_name}</b>.</p>
    <p><b>Status:</b> {escape(status)}</p>
    <p><b>Title:</b> {title}</p>
    <blockquote style="border-left:3px solid #1389b1;padding-left:12px;color:#0b3a52">{body}</blockquote>
    """


def contact_ack_html(msg):
    message = linebreaks(escape(msg.message))
    return f"""
    <div style="font-family:system-ui,sans-serif;max-width:560px;color:#0b3a52">
      <h2 style="color:#0b6a8a">Thanks {escape(msg.name)}!</h2>
      <p>We got your message and will reply within one business day. For urgent bookings, call us or reply to this email.</p>
      <hr><p style="color:#666;font-size:12px">Your message:<br>{message}</p>
    </div>
    """


def contact_reply_html(msg, body):
    safe_body = linebreaks(escape(body))
    safe_original = linebreaks(escape(msg.message))
    return f"""
    <div style="font-family:system-ui,sans-serif;max-width:620px;color:#0b3a52;line-height:1.5">
      <h2 style="color:#0b6a8a">Dolphin Island Tours</h2>
      {safe_body}
      <hr style="border:none;border-top:1px solid #dbeafe;margin:24px 0">
      <p style="color:#64748b;font-size:13px;margin-bottom:8px"><b>Your original message:</b></p>
      <blockquote style="border-left:3px solid #1389b1;padding-left:12px;color:#334155;margin-left:0">
        {safe_original}
      </blockquote>
    </div>
    """


def promotional_email_html(body, cta_label="", cta_url=""):
    safe_body = linebreaks(escape(body))
    button = ""
    if cta_label and cta_url:
        button = f"""
        <p style="margin:24px 0">
          <a href="{escape(cta_url)}"
             style="background:#0b6a8a;color:#fff;text-decoration:none;padding:12px 18px;border-radius:999px;display:inline-block;font-weight:700">
             {escape(cta_label)}
          </a>
        </p>
        """
    return f"""
    <div style="font-family:system-ui,sans-serif;max-width:620px;color:#0b3a52;line-height:1.55">
      <h2 style="color:#0b6a8a">Dolphin Island Tours</h2>
      {safe_body}
      {button}
      <hr style="border:none;border-top:1px solid #dbeafe;margin:24px 0">
      <p style="color:#64748b;font-size:12px">
        You are receiving this because you contacted or booked with Dolphin Island Tours.<br>
        <a href="{{{{ unsubscribe_url }}}}" style="color:#1389b1;text-decoration:none">Unsubscribe from these emails</a>
      </p>
    </div>
    """


def campaign_email_html(body, name="", promo_code="", cta_label="", cta_url="", subject_line=""):
    # Substitute placeholders BEFORE escaping so they actually match.
    name_str = (name or "there").strip() or "there"
    filled = body.replace("{name}", name_str).replace("{promo_code}", promo_code or "")
    # Convert literal escape sequences typed in textarea ("\n", "\r", "\t") to real chars.
    filled = filled.replace("\\r\\n", "\n").replace("\\n", "\n").replace("\\t", "  ")
    safe_body = linebreaks(escape(filled))
    promo_block = ""
    if promo_code:
        promo_block = f"""
        <div style="background:#eef9fd;border:1px dashed #1389b1;border-radius:12px;padding:14px;text-align:center;margin:20px 0">
          <div style="font-size:12px;color:#0b6a8a;text-transform:uppercase;letter-spacing:0.15em">Your promo code</div>
          <div style="font-size:28px;font-weight:800;letter-spacing:0.1em;color:#0b3a52;margin-top:4px">{escape(promo_code)}</div>
          <div style="font-size:12px;color:#475569;margin-top:6px">Apply at checkout.</div>
        </div>
        """
    button = ""
    if cta_label and cta_url:
        button = f"""
        <p style="margin:20px 0">
          <a href="{escape(cta_url)}"
             style="background:#0b6a8a;color:#fff;text-decoration:none;padding:12px 18px;border-radius:999px;display:inline-block;font-weight:700">
             {escape(cta_label)}
          </a>
        </p>
        """
    return f"""
    <div style="font-family:system-ui,sans-serif;max-width:620px;margin:0 auto;color:#0b3a52;line-height:1.55">
      <h2 style="color:#0b6a8a;margin-bottom:4px">Dolphin Island Tours</h2>
      {f'<p style="color:#64748b;margin-top:0">{escape(subject_line)}</p>' if subject_line else ''}
      {safe_body}
      {promo_block}
      {button}
      <hr style="border:none;border-top:1px solid #dbeafe;margin:24px 0">
      <p style="color:#64748b;font-size:12px">
        Sent by Dolphin Island Tours · 2700 Harbortown Drive, Merritt Island, FL.
        You're receiving this because you booked, signed up, or subscribed.<br>
        <a href="{{{{ unsubscribe_url }}}}" style="color:#1389b1;text-decoration:none">Unsubscribe from these emails</a>
      </p>
    </div>
    """


def password_reset_html(reset_url, name=""):
    safe_name = escape(name or "there")
    return f"""
    <div style="font-family:system-ui,sans-serif;max-width:560px;margin:0 auto;color:#0b3a52;line-height:1.55">
      <h2 style="color:#0b6a8a">Reset your password</h2>
      <p>Hi {safe_name}, we got a request to reset your password for Dolphin Island Tours.</p>
      <p>
        <a href="{escape(reset_url)}"
           style="background:#0b6a8a;color:#fff;text-decoration:none;padding:12px 18px;border-radius:999px;display:inline-block;font-weight:700">
          Reset password
        </a>
      </p>
      <p style="color:#475569;font-size:13px">Or paste this link in your browser:<br>
      <span style="word-break:break-all">{escape(reset_url)}</span></p>
      <p style="color:#475569;font-size:13px">The link expires in 24 hours.
      If you didn't request this, you can ignore this email.</p>
    </div>
    """


def booking_cancelled_html(booking, reason, alternatives=None):
    customer_name = escape(booking.customer_name)
    tour_name = escape(booking.slot.tour.name)
    slot_date = escape(str(booking.slot.date))
    slot_time = escape(str(booking.slot.time))
    alt_html = ""
    if alternatives:
        rows = "".join(
            f"<li>{escape(str(s['date']))} at {escape(str(s['time']))} - {escape(str(s['seats_remaining']))} seats</li>"
            for s in alternatives[:8]
        )
        alt_html = f"""
        <p><b>Other available departures for {tour_name}:</b></p>
        <ul>{rows}</ul>
        <p>Reply to this email with the date/time you'd like and we'll move your booking - no extra charge.</p>
        """
    return f"""
    <div style="font-family:system-ui,sans-serif;max-width:560px;color:#0b3a52">
      <h2 style="color:#b91c1c">Your tour was cancelled</h2>
      <p>Hi {customer_name}, we're sorry - we had to cancel your {tour_name}
      on {slot_date} at {slot_time}.</p>
      <p><b>Reason:</b> {escape(reason)}</p>
      {alt_html}
      <hr>
      <p><b>Booking #:</b> {escape(str(booking.id))}<br>
      <b>Party:</b> {booking.party_size} guests<br>
      <b>Amount paid:</b> ${booking.total_cents/100:.2f} - full refund will be processed within 5-7 business days.</p>
      <p>Questions? Reply to this email or contact lewis@dolphinislandtours.com.</p>
    </div>
    """


def admin_notify_html(booking):
    return f"""
    <h3>New booking</h3>
    <p>{escape(booking.customer_name)} ({escape(booking.customer_email)}) booked {booking.party_size} guests
    for {escape(str(booking.slot.date))} {escape(str(booking.slot.time))}. Total ${booking.total_cents/100:.2f}.</p>
    <p>Phone: {escape(booking.customer_phone or 'n/a')}<br>
    Notes: {linebreaks(escape(booking.special_requests or 'none'))}</p>
    """
