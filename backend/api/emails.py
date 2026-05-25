import smtplib
import ssl
from email.message import EmailMessage
import requests
from django.conf import settings
from django.utils.html import escape, linebreaks


def _send_via_smtp(to, subject, html):
    recipients = [to] if isinstance(to, str) else list(to)
    msg = EmailMessage()
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject
    msg.set_content("This email requires an HTML-capable client.")
    msg.add_alternative(html, subtype="html")
    ctx = ssl.create_default_context()
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as s:
        s.ehlo()
        s.starttls(context=ctx)
        s.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        s.send_message(msg)
    return {"id": "smtp-sent", "to": recipients}


def send_email(to, subject, html):
    """Send via Gmail SMTP if configured, else Resend, else noop."""
    if getattr(settings, "SMTP_HOST", "") and getattr(settings, "SMTP_USER", ""):
        return _send_via_smtp(to, subject, html)
    if not settings.RESEND_API_KEY:
        print(f"[email:noop] to={to} subject={subject}")
        return None
    r = requests.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {settings.RESEND_API_KEY}", "Content-Type": "application/json"},
        json={"from": settings.EMAIL_FROM, "to": [to] if isinstance(to, str) else to,
              "subject": subject, "html": html},
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
        You are receiving this because you contacted or booked with Dolphin Island Tours.
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
        You're receiving this because you booked, signed up, or subscribed.
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
