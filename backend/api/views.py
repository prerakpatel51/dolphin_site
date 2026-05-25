from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import transaction
from django.db.models import Avg, Count, F, IntegerField, Q, Sum, Value
from django.db.models.functions import Coalesce
from decimal import Decimal, ROUND_HALF_UP
from datetime import timedelta
from rest_framework import viewsets, mixins
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from django.http import HttpResponse
from django.utils import timezone
from django.utils.html import escape
from .models import (Tour, TourSlot, Booking, SiteSettings, SiteImage, ContactMessage,
                     ActivityLog, PageContent, PromoCode, Review)
from .serializers import (UserSerializer, TourSerializer, TourSlotSerializer, BookingSerializer,
                          BookingCreateSerializer, SiteSettingsSerializer, SiteImageSerializer,
                          ContactMessageSerializer, PageContentSerializer, PromoValidateSerializer,
                          ReviewSerializer, ReviewCreateSerializer)
from .emails import send_email, booking_receipt_html, admin_notify_html, contact_admin_html, contact_ack_html
from .payments import charge

User = get_user_model()
BOOKED_STATUSES = ["paid", "pending"]
PAYMENT_FAILED_MESSAGE = (
    "Your card was declined or could not be charged. No charge was made and your booking "
    "was not confirmed. Please try another card."
)


def set_auth_cookies(response, refresh):
    access = refresh.access_token
    cookie_kwargs = {
        "httponly": True,
        "secure": settings.JWT_COOKIE_SECURE,
        "samesite": settings.JWT_COOKIE_SAMESITE,
        "path": "/api/",
    }
    response.set_cookie(
        "access_token",
        str(access),
        max_age=int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()),
        **cookie_kwargs,
    )
    response.set_cookie(
        "refresh_token",
        str(refresh),
        max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
        **cookie_kwargs,
    )
    return response


def clear_auth_cookies(response):
    for name in ("access_token", "refresh_token"):
        response.delete_cookie(
            name,
            path="/api/",
            samesite=settings.JWT_COOKIE_SAMESITE,
            secure=settings.JWT_COOKIE_SECURE,
        )
    return response


def with_booked_seats(qs):
    return qs.annotate(
        booked_seats=Coalesce(
            Sum("bookings__party_size", filter=Q(bookings__status__in=BOOKED_STATUSES)),
            Value(0),
            output_field=IntegerField(),
        )
    )


def expire_stale_pending_bookings():
    minutes = max(1, int(getattr(settings, "PENDING_BOOKING_EXPIRY_MINUTES", 15)))
    cutoff = timezone.now() - timedelta(minutes=minutes)
    expired = Booking.objects.filter(status="pending", updated_at__lt=cutoff).update(status="expired")
    if expired:
        ActivityLog.log(
            "booking.pending_expired",
            f"Expired {expired} pending booking hold{'s' if expired != 1 else ''}.",
            level="info",
            actor="system",
            count=expired,
        )
    return expired


def client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def rate_limited(request, scope, identifier="", limit=10, window=300):
    key = f"rate:{scope}:{client_ip(request)}:{identifier}".lower()
    try:
        count = cache.incr(key)
    except ValueError:
        cache.add(key, 1, timeout=window)
        count = 1
    return count > limit


def tax_cents_for(amount_cents, tax_rate_percent):
    rate = Decimal(str(tax_rate_percent or 0))
    if rate <= 0 or amount_cents <= 0:
        return 0
    return int((Decimal(amount_cents) * rate / Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if rate_limited(request, "signup", limit=5, window=10 * 60):
            return Response({"detail": "Too many signup attempts. Try again later."}, status=429)
        s = UserSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = s.save()
        return Response(UserSerializer(user).data, status=201)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenObtainPairSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        refresh = RefreshToken(serializer.validated_data["refresh"])
        response = Response({"ok": True})
        return set_auth_cookies(response, refresh)


class RefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.COOKIES.get("refresh_token")
        if not token:
            return Response({"detail": "Refresh token is missing."}, status=401)
        try:
            refresh = RefreshToken(token)
        except Exception:
            response = Response({"detail": "Refresh token is invalid or expired."}, status=401)
            return clear_auth_cookies(response)
        response = Response({"ok": True})
        return set_auth_cookies(response, refresh)


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        return clear_auth_cookies(Response(status=204))


class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        s = UserSerializer(request.user, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data)

    def delete(self, request):
        request.user.delete()
        return Response(status=204)


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
    )
    by_date = {}
    for s in qs:
        if s.seats_remaining <= 0:
            continue
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


class BookingViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        expire_stale_pending_bookings()
        return Booking.objects.filter(user=self.request.user)

    @action(detail=False, methods=["post"], url_path="create-and-pay")
    @transaction.atomic
    def create_and_pay(self, request):
        """Create booking + charge Square in one shot."""
        if rate_limited(request, "booking_create", str(request.user.pk), limit=10, window=10 * 60):
            return Response({"detail": "Too many booking attempts. Try again later."}, status=429)
        expire_stale_pending_bookings()
        create_ser = BookingCreateSerializer(data=request.data)
        create_ser.is_valid(raise_exception=True)
        data = create_ser.validated_data
        try:
            locked_slot = (TourSlot.objects.select_for_update()
                           .select_related("tour")
                           .get(pk=data["slot"].pk, is_active=True))
        except TourSlot.DoesNotExist:
            return Response({"slot_id": "This departure is no longer bookable."}, status=400)
        if locked_slot.date < timezone.now().date():
            return Response({"slot_id": "This departure is no longer bookable."}, status=400)
        if data["party_size"] > locked_slot.seats_remaining:
            return Response({"party_size": f"Only {locked_slot.seats_remaining} seats remaining."}, status=400)
        data["slot"] = locked_slot

        source_id = request.data.get("source_id")
        if not source_id and not settings.FAKE_PAYMENTS:
            ActivityLog.log("booking.missing_source", "No payment source", level="warn",
                             actor=request.user.email)
            return Response({"detail": "Missing payment source_id."}, status=400)

        price = data["slot"].tour.price_per_person * 100
        subtotal = price * data["party_size"]

        promo_obj = None
        discount = 0
        promo_str = (request.data.get("promo_code") or "").strip()
        if promo_str:
            try:
                pc = PromoCode.objects.select_for_update().get(code__iexact=promo_str)
                promo_email = request.user.email if request.user.is_authenticated else data["customer_email"]
                ok, reason = pc.is_redeemable(email=promo_email)
                if not ok:
                    return Response({"promo_code": reason}, status=400)
                promo_obj = pc
                discount = pc.discount_for(subtotal)
            except PromoCode.DoesNotExist:
                return Response({"promo_code": "Invalid promo code."}, status=400)
        taxable_total = max(0, subtotal - discount)
        site_settings = SiteSettings.get()
        tax = tax_cents_for(taxable_total, site_settings.tax_rate_percent)
        total = taxable_total + tax

        booking = Booking.objects.create(
            user=request.user,
            slot=data["slot"],
            party_size=data["party_size"],
            price_per_person_cents=price,
            tax_cents=tax,
            total_cents=total,
            customer_name=data["customer_name"],
            customer_email=data["customer_email"],
            customer_phone=data.get("customer_phone", ""),
            travelers=data.get("travelers", []),
            special_requests=data.get("special_requests", ""),
            promo_code=promo_obj,
            discount_cents=discount,
            status="pending",
        )

        if settings.FAKE_PAYMENTS:
            payment = {"id": f"FAKE-{booking.id}", "order_id": "FAKE-ORDER"}
            ActivityLog.log("booking.fake_paid", "FAKE_PAYMENTS bypass active",
                             level="warn", actor=request.user.email, booking_id=str(booking.id))
        else:
            try:
                payment = charge(source_id, total, data["customer_email"],
                                 note=f"Dolphin tour {data['slot'].date} {data['slot'].time}")
            except Exception as e:
                booking.status = "payment_failed"
                booking.save(update_fields=["status", "updated_at"])
                ActivityLog.log("booking.payment_failed", str(e), level="error",
                                 actor=request.user.email, booking_id=str(booking.id))
                return Response({"detail": PAYMENT_FAILED_MESSAGE}, status=402)

        booking.square_payment_id = payment.get("id", "")
        booking.square_order_id = payment.get("order_id", "")
        booking.status = "paid"
        booking.save()

        try:
            send_email(booking.customer_email, "Your Dolphin Island Tours booking", booking_receipt_html(booking))
            send_email(settings.ADMIN_EMAIL, f"New booking: {booking.customer_name}", admin_notify_html(booking))
            ActivityLog.log("booking.email_sent", f"Receipts sent for {booking.id}",
                             level="success", actor=request.user.email)
        except Exception as e:
            ActivityLog.log("booking.email_failed", str(e), level="warn",
                             actor=request.user.email, booking_id=str(booking.id))

        if promo_obj:
            promo_obj.used_count = F("used_count") + 1
            promo_obj.save(update_fields=["used_count"])
            ActivityLog.log("promo.redeemed", f"{promo_obj.code} – ${discount/100:.2f} off",
                             level="info", actor=request.user.email, code=promo_obj.code)

        ActivityLog.log("booking.paid", f"{booking.customer_name} · ${booking.total_cents/100:.2f}",
                         level="success", actor=request.user.email,
                         booking_id=str(booking.id), party=booking.party_size)
        return Response(BookingSerializer(booking).data, status=201)


class ReviewViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [AllowAny]

    def get_queryset(self):
        from django.db.models import Q
        slug = self.request.query_params.get("tour")
        featured = self.request.query_params.get("featured")
        filt = Q(is_approved=True)
        # Authenticated users also see their own pending review.
        if self.request.user.is_authenticated:
            filt |= Q(user=self.request.user)
        qs = Review.objects.filter(filt).select_related("tour", "user").distinct()
        if slug:
            qs = qs.filter(tour__slug=slug)
        if featured == "1":
            qs = qs.filter(is_featured=True, is_approved=True)
        return qs

    def get_serializer_class(self):
        return ReviewCreateSerializer if self.action == "create" else ReviewSerializer

    def create(self, request, *args, **kwargs):
        ser = ReviewCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        slug = ser.validated_data.get("tour_slug", "")
        tour = None
        if slug:
            try:
                tour = Tour.objects.get(slug=slug)
            except Tour.DoesNotExist:
                pass
        user = request.user if request.user.is_authenticated else None
        # One review per user+tour
        if user and tour and Review.objects.filter(user=user, tour=tour).exists():
            return Response({"detail": "You already reviewed this tour."}, status=400)
        # Optional: also dedupe anonymous submissions by email + tour
        if not user and tour and ser.validated_data.get("author_email"):
            if Review.objects.filter(tour=tour, author_email__iexact=ser.validated_data["author_email"]).exists():
                return Response({"detail": "A review from this email already exists for this tour."}, status=400)

        review = ser.save()
        review.user = user
        # Auto-approve if user has a paid booking for this tour
        if user and tour and Booking.objects.filter(user=user, slot__tour=tour, status="paid").exists():
            review.is_approved = True
            review.booking = Booking.objects.filter(user=user, slot__tour=tour, status="paid").order_by("-created_at").first()
        review.save()
        ActivityLog.log("review.submitted", f"{review.author_name} – {review.rating}★ – {'auto-approved' if review.is_approved else 'pending'}",
                         level="info", actor=(user.email if user else review.author_email or "anonymous"),
                         tour=tour.slug if tour else "")
        return Response({
            "ok": True,
            "pending_moderation": not review.is_approved,
            "review": ReviewSerializer(review).data,
        }, status=201)


@api_view(["GET"])
@permission_classes([AllowAny])
def tour_review_stats(request, slug):
    qs = Review.objects.filter(is_approved=True, tour__slug=slug)
    summary = qs.aggregate(total=Count("id"), average=Avg("rating"))
    total = summary["total"] or 0
    if total == 0:
        return Response({"count": 0, "average": 0, "breakdown": {}})
    rows = qs.values("rating").annotate(total=Count("id"))
    breakdown = {str(i): 0 for i in range(1, 6)}
    breakdown.update({str(row["rating"]): row["total"] for row in rows})
    return Response({"count": total, "average": round(summary["average"] or 0, 2), "breakdown": breakdown})


@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset_request(request):
    """Always returns 200 to avoid leaking which emails exist."""
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.http import urlsafe_base64_encode
    from django.utils.encoding import force_bytes
    from .emails import send_email, password_reset_html

    email = (request.data.get("email") or "").strip().lower()
    if rate_limited(request, "password_reset", email or "blank", limit=5, window=10 * 60):
        return Response({"detail": "Too many reset requests. Try again later."}, status=429)
    if email:
        try:
            user = User.objects.get(email__iexact=email)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            frontend = settings.FRONTEND_URL.rstrip("/")
            reset_url = f"{frontend}/reset-password?uid={uidb64}&token={token}"
            try:
                send_email(user.email, "Reset your Dolphin Island Tours password",
                           password_reset_html(reset_url, name=user.first_name))
                ActivityLog.log("auth.reset_requested", email, level="info", actor=email)
            except Exception as e:
                ActivityLog.log("auth.reset_email_failed", f"{email}: {e}", level="error", actor=email)
        except User.DoesNotExist:
            ActivityLog.log("auth.reset_no_user", email, level="info", actor=email)
    return Response({"ok": True}, status=200)


@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.http import urlsafe_base64_decode
    from django.contrib.auth.password_validation import validate_password
    from django.core.exceptions import ValidationError

    uid = request.data.get("uid", "")
    token = request.data.get("token", "")
    new_pw = request.data.get("password", "")
    if not uid or not token or not new_pw:
        return Response({"detail": "Missing fields."}, status=400)
    try:
        pk = int(urlsafe_base64_decode(uid).decode())
        user = User.objects.get(pk=pk)
    except Exception:
        return Response({"detail": "Invalid reset link."}, status=400)
    if not default_token_generator.check_token(user, token):
        return Response({"detail": "Reset link is invalid or expired."}, status=400)
    try:
        validate_password(new_pw, user=user)
    except ValidationError as e:
        return Response({"password": e.messages}, status=400)
    user.set_password(new_pw)
    user.save()
    ActivityLog.log("auth.reset_completed", user.email, level="success", actor=user.email)
    return Response({"ok": True})


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
        s = SiteSettings.get()
        data = SiteSettingsSerializer(s).data
        images = {si.key: SiteImageSerializer(si).data for si in SiteImage.objects.all()}
        data["images"] = images
        pages = {p.page: PageContentSerializer(p).data for p in PageContent.objects.select_related("hero_image")}
        data["pages"] = pages
        return Response(data)


class ContactView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if rate_limited(request, "contact", limit=5, window=10 * 60):
            return Response({"detail": "Too many contact submissions. Try again later."}, status=429)
        ser = ContactMessageSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        msg = ser.save()
        ActivityLog.log("contact.received", f"{msg.name} <{msg.email}>", level="info",
                         actor=msg.email, subject=msg.subject)
        try:
            send_email(settings.ADMIN_EMAIL, f"New inquiry from {msg.name}", contact_admin_html(msg))
            send_email(msg.email, "We got your message – Dolphin Island Tours", contact_ack_html(msg))
        except Exception as e:
            ActivityLog.log("contact.email_failed", str(e), level="warn", actor=msg.email)
        return Response({"ok": True}, status=201)


@api_view(["GET"])
@permission_classes([AllowAny])
def sitemap_xml(request):
    configured_frontend = settings.FRONTEND_URL.rstrip("/")
    base = request.build_absolute_uri("/").rstrip("/") if configured_frontend.endswith(":5173") else configured_frontend
    urls = [
        (f"{base}/", "daily", "1.0"),
        (f"{base}/tours", "daily", "0.9"),
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
    return HttpResponse(body, content_type="application/xml")


@api_view(["GET"])
@permission_classes([AllowAny])
def robots_txt(request):
    configured = SiteSettings.get().robots_txt.strip()
    configured_frontend = settings.FRONTEND_URL.rstrip("/")
    base = request.build_absolute_uri("/").rstrip("/") if configured_frontend.endswith(":5173") else configured_frontend
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
    return HttpResponse(configured + "\n", content_type="text/plain")


@api_view(["GET"])
@permission_classes([AllowAny])
def config(request):
    site_settings = SiteSettings.get()
    return Response({
        "price_per_person": settings.PRICE_PER_PERSON,
        "min_party": settings.MIN_PARTY,
        "max_party": settings.MAX_PARTY,
        "tax_rate_percent": str(site_settings.tax_rate_percent),
        "square_app_id": settings.SQUARE_APP_ID,
        "square_location_id": settings.SQUARE_LOCATION_ID,
        "square_env": settings.SQUARE_ENV,
        "fake_payments": settings.FAKE_PAYMENTS,
    })
