from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core import signing
from django.db import IntegrityError, transaction
from django.db.models import F, IntegerField, Q, Sum, Value
from django.db.models.functions import Coalesce, Greatest
from decimal import Decimal, ROUND_HALF_UP
from datetime import timedelta
from rest_framework import viewsets, mixins
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from django.http import HttpResponse
from django.utils import timezone
from django.utils.html import escape
from django.views.decorators.http import require_http_methods
from .models import (Tour, TourSlot, Booking, SiteSettings, SiteImage, ContactMessage,
                     PageContent, NavigationLink, FAQItem, PromoCode, MailingListEntry,
                     ActivityLog, SITE_PAYLOAD_CACHE_KEY, RateLimitBucket)
from .serializers import (TourSerializer, TourSlotSerializer, BookingSerializer,
                          BookingCreateSerializer, SiteSettingsSerializer, SiteImageSerializer,
                          ContactMessageSerializer, PageContentSerializer, NavigationLinkSerializer, FAQItemSerializer,
                          PromoValidateSerializer, BookingLookupSerializer, BookingLookupResultSerializer)
from .emails import (send_email, booking_receipt_html, admin_notify_html, contact_admin_html,
                     contact_ack_html)
from .email_queue import enqueue_transactional_email
from .payments import charge
import hashlib
import logging
import os

User = get_user_model()
logger = logging.getLogger(__name__)
BOOKED_STATUSES = ["paid", "pending"]
PAYMENT_FAILED_MESSAGE = (
    "Your card was declined or could not be charged. No charge was made and your booking "
    "was not confirmed. Please try another card."
)


def with_booked_seats(qs):
    return qs.annotate(
        booked_seats=Coalesce(
            Sum("bookings__party_size", filter=Q(bookings__status__in=BOOKED_STATUSES)),
            Value(0),
            output_field=IntegerField(),
        )
    )


def release_promo_holds(promo_ids):
    """Give back the reserved use on each promo (clamped at zero)."""
    from collections import Counter

    for promo_id, count in Counter(pid for pid in promo_ids if pid).items():
        PromoCode.objects.filter(pk=promo_id).update(
            used_count=Greatest(F("used_count") - count, Value(0), output_field=IntegerField())
        )


def expire_pending_holds():
    """Expire stale pending bookings and release the promo uses they reserved."""
    minutes = max(1, int(getattr(settings, "PENDING_BOOKING_EXPIRY_MINUTES", 15)))
    cutoff = timezone.now() - timedelta(minutes=minutes)
    with transaction.atomic():
        stale = (Booking.objects.select_for_update()
                 .filter(status="pending", updated_at__lt=cutoff))
        promo_ids = list(stale.values_list("promo_code_id", flat=True))
        expired = stale.update(status="expired")
        # Expired holds never paid, so return the promo use they reserved.
        release_promo_holds(promo_ids)
    return expired


def expire_stale_pending_bookings():
    interval = max(1, int(getattr(settings, "PENDING_BOOKING_EXPIRY_CHECK_SECONDS", 30)))
    if not cache.add("pending-booking-expiry-lock", "1", timeout=interval):
        return 0
    return expire_pending_holds()


def client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def normalized_client_ip(request):
    ip = client_ip(request)
    if ip == "unknown":
        return None
    return ip


def rate_limited(request, scope, identifier="", limit=10, window=300):
    raw_key = f"{scope}:{client_ip(request)}:{identifier}".lower()
    key = f"rate:{scope}:{hashlib.sha256(raw_key.encode('utf-8')).hexdigest()}"
    now = timezone.now()
    expires_at = now + timedelta(seconds=window)

    try:
        with transaction.atomic():
            bucket = RateLimitBucket.objects.select_for_update().filter(key=key).first()
            if bucket is None:
                RateLimitBucket.objects.create(key=key, count=1, expires_at=expires_at)
                return False
            if bucket.expires_at <= now:
                bucket.count = 1
                bucket.expires_at = expires_at
                bucket.save(update_fields=["count", "expires_at", "updated_at"])
                return False
            bucket.count += 1
            bucket.save(update_fields=["count", "updated_at"])
            return bucket.count > limit
    except IntegrityError:
        with transaction.atomic():
            bucket = RateLimitBucket.objects.select_for_update().get(key=key)
            if bucket.expires_at <= now:
                bucket.count = 1
                bucket.expires_at = expires_at
                bucket.save(update_fields=["count", "expires_at", "updated_at"])
                return False
            bucket.count += 1
            bucket.save(update_fields=["count", "updated_at"])
            return bucket.count > limit


def tax_cents_for(amount_cents, tax_rate_percent):
    rate = Decimal(str(tax_rate_percent or 0))
    if rate <= 0 or amount_cents <= 0:
        return 0
    return int((Decimal(amount_cents) * rate / Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


class TourViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Tour.objects.filter(is_active=True)
    serializer_class = TourSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"


@api_view(["GET"])
@permission_classes([AllowAny])
def tour_dates(request, slug):
    """Return dates that have at least one bookable slot, grouped per date."""
    expire_stale_pending_bookings()
    qs = with_booked_seats(
        TourSlot.objects.filter(tour__slug=slug, is_active=True,
                                date__gte=timezone.now().date())
        .select_related("tour")
        .order_by("date", "time")
    ).filter(booked_seats__lt=F("capacity"))
    by_date = {}
    for s in qs:
        by_date.setdefault(s.date.isoformat(), []).append({
            "id": s.id, "time": s.time.strftime("%H:%M"),
            "seats_remaining": s.seats_remaining,
        })
    return Response({"dates": by_date})


class TourSlotViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = TourSlot.objects.filter(is_active=True)
    serializer_class = TourSlotSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        expire_stale_pending_bookings()
        qs = super().get_queryset()
        from django.utils import timezone
        qs = qs.filter(date__gte=timezone.now().date()).select_related("tour")
        tour_slug = self.request.query_params.get("tour")
        if tour_slug:
            qs = qs.filter(tour__slug=tour_slug)
        return with_booked_seats(qs)


class BookingViewSet(viewsets.GenericViewSet):
    serializer_class = BookingSerializer
    permission_classes = [AllowAny]
    queryset = Booking.objects.none()

    @action(detail=False, methods=["post"], url_path="create-and-pay")
    def create_and_pay(self, request):
        """Reserve a pending booking, charge Square, then confirm.

        Seats and any promo use are reserved inside a short transaction so the
        external payment call does not hold row locks. If the charge fails the
        hold is released; expired holds are released by
        ``expire_stale_pending_bookings``.
        """
        expire_stale_pending_bookings()
        create_ser = BookingCreateSerializer(data=request.data)
        create_ser.is_valid(raise_exception=True)
        data = create_ser.validated_data
        rate_identifier = str(request.user.pk) if request.user.is_authenticated else data["customer_email"].lower()
        if rate_limited(request, "booking_create", rate_identifier, limit=10, window=10 * 60):
            return Response({"detail": "Too many booking attempts. Try again later."}, status=429)

        source_id = request.data.get("source_id")
        if not source_id and not settings.FAKE_PAYMENTS:
            return Response({"detail": "Missing payment source_id."}, status=400)

        promo_str = (request.data.get("promo_code") or "").strip()
        promo_email = request.user.email if request.user.is_authenticated else data["customer_email"]

        # ---- Reserve seats + promo hold in a short transaction (no payment yet). ----
        try:
            with transaction.atomic():
                locked_slot = (TourSlot.objects.select_for_update()
                               .select_related("tour")
                               .get(pk=data["slot"].pk, is_active=True))
                if locked_slot.date < timezone.now().date():
                    return Response({"slot_id": "This departure is no longer bookable."}, status=400)
                if data["party_size"] > locked_slot.seats_remaining:
                    return Response({"party_size": f"Only {locked_slot.seats_remaining} seats remaining."}, status=400)

                price = locked_slot.tour.price_per_person * 100
                subtotal = price * data["party_size"]
                tax_rate_percent = locked_slot.tour.tax_rate_percent

                promo_obj = None
                discount = 0
                if promo_str:
                    try:
                        pc = PromoCode.objects.select_for_update().get(code__iexact=promo_str)
                    except PromoCode.DoesNotExist:
                        return Response({"promo_code": "Invalid promo code."}, status=400)
                    except PromoCode.MultipleObjectsReturned:
                        logger.error("Duplicate promo codes share the spelling %r.", promo_str)
                        return Response({"promo_code": "Invalid promo code."}, status=400)
                    ok, reason = pc.is_redeemable(email=promo_email)
                    if not ok:
                        return Response({"promo_code": reason}, status=400)
                    promo_obj = pc
                    discount = pc.discount_for(subtotal)

                taxable_total = max(0, subtotal - discount)
                tax = tax_cents_for(taxable_total, tax_rate_percent)
                total = taxable_total + tax

                first_name = data["customer_first_name"]
                last_name = data["customer_last_name"]
                booking = Booking.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    slot=locked_slot,
                    party_size=data["party_size"],
                    price_per_person_cents=price,
                    tax_cents=tax,
                    total_cents=total,
                    customer_first_name=first_name,
                    customer_last_name=last_name,
                    customer_name=f"{first_name} {last_name}".strip(),
                    customer_email=data["customer_email"],
                    customer_phone=data.get("customer_phone", ""),
                    travelers=data.get("travelers", []),
                    special_requests=data.get("special_requests", ""),
                    promo_code=promo_obj,
                    discount_cents=discount,
                    status="pending",
                )
                if promo_obj:
                    # Reserve the redemption now so concurrent single-use
                    # attempts are blocked while this booking is paid for.
                    PromoCode.objects.filter(pk=promo_obj.pk).update(used_count=F("used_count") + 1)
        except TourSlot.DoesNotExist:
            return Response({"slot_id": "This departure is no longer bookable."}, status=400)

        # ---- Charge outside the transaction so no row locks are held. ----
        if settings.FAKE_PAYMENTS:
            payment = {"id": f"FAKE-{booking.id}", "order_id": "FAKE-ORDER"}
        else:
            try:
                payment = charge(
                    source_id,
                    total,
                    data["customer_email"],
                    note=f"Dolphin tour {locked_slot.date} {locked_slot.time}",
                    subtotal_cents=subtotal,
                    discount_cents=discount,
                    tax_cents=tax,
                    tax_rate_percent=tax_rate_percent,
                    item_name=locked_slot.tour.name,
                )
            except Exception as e:
                logger.exception("Payment failed for booking %s.", booking.id)
                with transaction.atomic():
                    Booking.objects.filter(pk=booking.pk).update(status="payment_failed", updated_at=timezone.now())
                    if promo_obj:
                        release_promo_holds([promo_obj.pk])
                ActivityLog.log(
                    "booking_payment_failed",
                    actor=request.user.email if request.user.is_authenticated else data["customer_email"],
                    message=f"Payment failed for booking {booking.id}.",
                    metadata={
                        "booking_id": str(booking.id),
                        "customer_email": data["customer_email"],
                        "total_cents": total,
                        "error": str(e),
                    },
                )
                return Response({"detail": PAYMENT_FAILED_MESSAGE}, status=402)

        # ---- Confirm the booking in a short transaction. ----
        with transaction.atomic():
            Booking.objects.filter(pk=booking.pk).update(
                square_payment_id=payment.get("id", ""),
                square_order_id=payment.get("order_id", ""),
                status="paid",
                updated_at=timezone.now(),
            )
        booking.refresh_from_db()
        logger.info("Payment verified for booking %s.", booking.id)
        ActivityLog.log(
            "booking_payment_verified",
            actor=request.user.email if request.user.is_authenticated else booking.customer_email,
            message=f"Booking {booking.id} payment was verified.",
            metadata={
                "booking_id": str(booking.id),
                "customer_email": booking.customer_email,
                "total_cents": booking.total_cents,
                "slot_id": booking.slot_id,
                "square_payment_id": booking.square_payment_id,
                "square_order_id": booking.square_order_id,
                "promo_code": promo_obj.code if promo_obj else "",
            },
        )

        try:
            enqueue_transactional_email(
                booking.customer_email,
                "Your Dolphin Island Tours booking",
                booking_receipt_html(booking),
                "booking_receipt",
            )
            enqueue_transactional_email(
                settings.ADMIN_EMAIL,
                f"New booking: {booking.customer_name}",
                admin_notify_html(booking),
                "booking_admin_notify",
            )
            logger.info("Booking confirmation emails queued for booking %s.", booking.id)
        except Exception:
            logger.exception("Booking confirmation email queueing failed for booking %s.", booking.id)

        return Response(BookingSerializer(booking).data, status=201)


@api_view(["POST"])
@permission_classes([AllowAny])
def booking_lookup(request):
    serializer = BookingLookupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data["email"].strip().lower()
    last_name = serializer.validated_data["last_name"].strip().lower()
    if rate_limited(request, "booking_lookup", email, limit=8, window=10 * 60):
        return Response({"detail": "Too many lookup attempts. Try again later."}, status=429)

    bookings = (
        Booking.objects.filter(customer_email__iexact=email)
        .select_related("slot__tour", "promo_code")
        .order_by("-created_at")
    )
    matches = []
    for booking in bookings:
        # Prefer the dedicated last-name field; fall back to the last token of
        # the full name for legacy bookings created before the field existed.
        booking_last = (booking.customer_last_name or "").strip().lower()
        if not booking_last:
            name_parts = (booking.customer_name or "").strip().split()
            booking_last = name_parts[-1].lower() if name_parts else ""
        if booking_last and booking_last == last_name:
            matches.append(booking)
    return Response({"results": BookingLookupResultSerializer(matches, many=True).data})


@api_view(["GET"])
@permission_classes([AllowAny])
def unsubscribe_marketing(request, token):
    try:
        data = signing.loads(token, salt="marketing-unsubscribe", max_age=60 * 60 * 24 * 365 * 5)
        email = (data.get("email") or "").strip().lower()
    except Exception:
        return HttpResponse("This unsubscribe link is invalid or expired.", status=400, content_type="text/plain")
    if not email:
        return HttpResponse("This unsubscribe link is invalid.", status=400, content_type="text/plain")
    User.objects.filter(email__iexact=email).update(accepts_marketing=False)
    MailingListEntry.objects.filter(email__iexact=email).update(subscribed=False)
    return HttpResponse(
        "You have been unsubscribed from Dolphin Island Tours marketing emails.",
        content_type="text/plain",
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def validate_promo(request):
    s = PromoValidateSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    code = s.validated_data["code"].strip()
    if rate_limited(request, "promo_validate", code or "blank", limit=20, window=5 * 60):
        return Response({"detail": "Too many promo code attempts. Try again later."}, status=429)
    try:
        pc = PromoCode.objects.get(code__iexact=code)
    except PromoCode.DoesNotExist:
        return Response({"valid": False, "reason": "Invalid code."}, status=200)
    except PromoCode.MultipleObjectsReturned:
        logger.error("Duplicate promo codes share the spelling %r.", code)
        return Response({"valid": False, "reason": "Invalid code."}, status=200)
    ok, reason = pc.is_redeemable(email=s.validated_data.get("email", ""))
    if not ok:
        return Response({"valid": False, "reason": reason}, status=200)
    discount = pc.discount_for(s.validated_data["subtotal_cents"])
    return Response({
        "valid": True,
        "code": pc.code,
        "kind": pc.kind,
        "percent_off": pc.percent_off,
        "amount_off_cents": pc.amount_off_cents,
        "discount_cents": discount,
        "label": pc.label,
    })


class SiteSettingsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        cached = cache.get(SITE_PAYLOAD_CACHE_KEY)
        if cached is not None:
            return Response(cached)
        s = SiteSettings.get()
        data = SiteSettingsSerializer(s).data
        images = {si.key: SiteImageSerializer(si).data for si in SiteImage.objects.all()}
        data["images"] = images
        pages = {
            p.page: PageContentSerializer(p).data
            for p in PageContent.objects.select_related("hero_image").prefetch_related("sections__image")
        }
        data["pages"] = pages
        nav_links = NavigationLink.objects.filter(is_active=True).order_by("area", "sort_order", "id")
        data["navigation"] = {
            "header": NavigationLinkSerializer([link for link in nav_links if link.area == "header"], many=True).data,
            "footer": NavigationLinkSerializer([link for link in nav_links if link.area == "footer"], many=True).data,
        }
        data["faqs"] = FAQItemSerializer(FAQItem.objects.filter(is_active=True).order_by("sort_order", "id"), many=True).data
        cache.set(SITE_PAYLOAD_CACHE_KEY, data, getattr(settings, "SITE_CACHE_SECONDS", 300))
        return Response(data)


class ContactView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if rate_limited(request, "contact", limit=5, window=10 * 60):
            return Response({"detail": "Too many contact submissions. Try again later."}, status=429)
        ser = ContactMessageSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        msg = ser.save()
        try:
            send_email(settings.ADMIN_EMAIL, f"New inquiry from {msg.name}", contact_admin_html(msg), include_unsubscribe=False)
            send_email(msg.email, "We got your message – Dolphin Island Tours", contact_ack_html(msg))
            logger.info("Contact form emails sent for message %s.", msg.pk)
        except Exception:
            logger.exception("Contact form email failed for message %s.", msg.pk)
        return Response({"ok": True}, status=201)


@require_http_methods(["GET", "HEAD"])
def sitemap_xml(request):
    configured_public_url = (os.getenv("PUBLIC_SITE_URL") or settings.FRONTEND_URL).rstrip("/")
    base = request.build_absolute_uri("/").rstrip("/") if configured_public_url.endswith(":5173") else configured_public_url
    urls = [
        (f"{base}/", "daily", "1.0"),
        (f"{base}/tours", "daily", "0.9"),
        (f"{base}/reviews", "weekly", "0.8"),
        (f"{base}/about", "monthly", "0.6"),
        (f"{base}/contact", "monthly", "0.7"),
    ]
    for t in Tour.objects.filter(is_active=True):
        urls.append((f"{base}/tours/{t.slug}", "weekly", "0.8"))
    body = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    today = timezone.now().date().isoformat()
    for url, changefreq, priority in urls:
        body += (
            "  <url>"
            f"<loc>{escape(url)}</loc>"
            f"<lastmod>{today}</lastmod>"
            f"<changefreq>{changefreq}</changefreq>"
            f"<priority>{priority}</priority>"
            "</url>\n"
        )
    body += "</urlset>"
    if request.method == "HEAD":
        return HttpResponse(content_type="application/xml")
    return HttpResponse(body, content_type="application/xml")


@require_http_methods(["GET", "HEAD"])
def robots_txt(request):
    configured = SiteSettings.get().robots_txt.strip()
    configured_public_url = (os.getenv("PUBLIC_SITE_URL") or settings.FRONTEND_URL).rstrip("/")
    base = request.build_absolute_uri("/").rstrip("/") if configured_public_url.endswith(":5173") else configured_public_url
    lines = []
    has_sitemap = False
    for line in configured.splitlines():
        if line.lower().startswith("sitemap:"):
            has_sitemap = True
            value = line.split(":", 1)[1].strip()
            if value.startswith("/"):
                lines.append(f"Sitemap: {base}{value}")
            elif value:
                lines.append(f"Sitemap: {value}")
            else:
                lines.append(f"Sitemap: {base}/sitemap.xml")
        else:
            lines.append(line)
    configured = "\n".join(lines)
    if not has_sitemap:
        configured = f"{configured}\nSitemap: {base}/sitemap.xml"
    if request.method == "HEAD":
        return HttpResponse(content_type="text/plain")
    return HttpResponse(configured + "\n", content_type="text/plain")


@api_view(["GET"])
@permission_classes([AllowAny])
def config(request):
    return Response({
        "price_per_person": settings.PRICE_PER_PERSON,
        "min_party": settings.MIN_PARTY,
        "max_party": settings.MAX_PARTY,
        "square_app_id": settings.SQUARE_APP_ID,
        "square_location_id": settings.SQUARE_LOCATION_ID,
        "square_env": settings.SQUARE_ENV,
        "fake_payments": settings.FAKE_PAYMENTS,
    })
