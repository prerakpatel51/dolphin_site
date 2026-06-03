from django.conf import settings
import logging
import requests
import uuid


logger = logging.getLogger(__name__)


SQUARE_API_VERSION = "2024-05-15"


def _money(amount_cents: int):
    return {"amount": int(amount_cents), "currency": "USD"}


def _square_request(path: str, body: dict):
    base_url = (
        "https://connect.squareupsandbox.com/v2"
        if settings.SQUARE_ENV == "sandbox"
        else "https://connect.squareup.com/v2"
    )
    response = requests.post(
        f"{base_url}{path}",
        headers={
            "Square-Version": SQUARE_API_VERSION,
            "Authorization": f"Bearer {settings.SQUARE_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        },
        json=body,
        timeout=30,
    )
    payload = response.json() if response.content else {}
    if response.status_code >= 400:
        errors = payload.get("errors") or [{"detail": response.text}]
        logger.error("Square API returned errors: %s", errors)
        raise RuntimeError("Square error: " + "; ".join(e.get("detail", str(e)) for e in errors))
    return payload


def _create_order(
    *,
    subtotal_cents: int,
    discount_cents: int,
    tax_cents: int,
    tax_rate_percent,
    item_name: str,
    note: str,
):
    order = {
        "location_id": settings.SQUARE_LOCATION_ID,
        "line_items": [
            {
                "uid": "tour",
                "name": item_name[:512],
                "quantity": "1",
                "base_price_money": _money(subtotal_cents),
            }
        ],
        "metadata": {"source": "dolphin-site"},
    }
    if note:
        order["line_items"][0]["note"] = note[:500]
    if discount_cents > 0:
        order["discounts"] = [
            {
                "uid": "booking-discount",
                "name": "Booking discount",
                "scope": "ORDER",
                "amount_money": _money(discount_cents),
            }
        ]
    if tax_cents > 0:
        order["taxes"] = [
            {
                "uid": "sales-tax",
                "name": "Sales tax",
                "scope": "ORDER",
                "percentage": str(tax_rate_percent),
            }
        ]
    payload = _square_request(
        "/orders",
        {
            "idempotency_key": str(uuid.uuid4()),
            "order": order,
        },
    )
    return payload["order"]["id"]


def charge(
    source_id: str,
    amount_cents: int,
    buyer_email: str,
    note: str = "",
    *,
    subtotal_cents: int | None = None,
    discount_cents: int = 0,
    tax_cents: int = 0,
    tax_rate_percent=0,
    item_name: str = "Dolphin Island Tours booking",
):
    """Charge a Square payment source and attach an itemized Square order."""
    if not settings.SQUARE_ACCESS_TOKEN:
        raise RuntimeError("Square not configured (set SQUARE_ACCESS_TOKEN).")

    subtotal_cents = amount_cents if subtotal_cents is None else subtotal_cents
    order_id = _create_order(
        subtotal_cents=subtotal_cents,
        discount_cents=discount_cents,
        tax_cents=tax_cents,
        tax_rate_percent=tax_rate_percent,
        item_name=item_name,
        note=note,
    )
    body = {
        "source_id": source_id,
        "idempotency_key": str(uuid.uuid4()),
        "amount_money": {"amount": amount_cents, "currency": "USD"},
        "location_id": settings.SQUARE_LOCATION_ID,
        "order_id": order_id,
        "buyer_email_address": buyer_email,
        "note": note[:500],
    }
    payload = _square_request("/payments", body)
    payment = payload["payment"]
    return {"id": payment.get("id", ""), "order_id": payment.get("order_id", order_id)}
