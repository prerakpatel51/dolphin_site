"""Square payment helpers. Lazy import so missing creds don't crash app."""
from django.conf import settings
import logging
import uuid


logger = logging.getLogger(__name__)


def charge(source_id: str, amount_cents: int, buyer_email: str, note: str = ""):
    """Charge a Square payment source (token from Web Payments SDK)."""
    if not settings.SQUARE_ACCESS_TOKEN:
        raise RuntimeError("Square not configured (set SQUARE_ACCESS_TOKEN).")

    try:
        from square.client import Client  # SDK <= 39
        client = Client(access_token=settings.SQUARE_ACCESS_TOKEN, environment=settings.SQUARE_ENV)
    except ImportError:
        from square import Square  # SDK >= 40
        from square.environment import SquareEnvironment
        env = SquareEnvironment.SANDBOX if settings.SQUARE_ENV == "sandbox" else SquareEnvironment.PRODUCTION
        client = Square(token=settings.SQUARE_ACCESS_TOKEN, environment=env)

    body = {
        "source_id": source_id,
        "idempotency_key": str(uuid.uuid4()),
        "amount_money": {"amount": amount_cents, "currency": "USD"},
        "location_id": settings.SQUARE_LOCATION_ID,
        "buyer_email_address": buyer_email,
        "note": note[:500],
    }

    # SDK <= 39
    if hasattr(client, "payments") and hasattr(client.payments, "create_payment"):
        result = client.payments.create_payment(body)
        if result.is_error():
            logger.error("Square payment API returned errors: %s", result.errors)
            raise RuntimeError("Square error: " + "; ".join(e.get("detail", str(e)) for e in result.errors))
        return result.body["payment"]

    # SDK >= 40
    result = client.payments.create(
        source_id=source_id,
        idempotency_key=body["idempotency_key"],
        amount_money={"amount": amount_cents, "currency": "USD"},
        location_id=settings.SQUARE_LOCATION_ID,
        buyer_email_address=buyer_email,
        note=note[:500],
    )
    payment = result.payment if hasattr(result, "payment") else result
    return {"id": getattr(payment, "id", ""), "order_id": getattr(payment, "order_id", "")}
