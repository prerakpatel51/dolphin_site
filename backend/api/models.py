from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import close_old_connections
from django.db.models.functions import Lower
from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver
from concurrent.futures import ThreadPoolExecutor
import logging
import uuid
import re


SITE_SETTINGS_CACHE_KEY = "site-settings:v1"
SITE_PAYLOAD_CACHE_KEY = "site-payload:v1"
REVIEW_STATS_CACHE_PREFIX = "tour-review-stats:v1:"
ALL_REVIEW_STATS_CACHE_KEY = "review-stats:v1:all"
logger = logging.getLogger(__name__)
_audit_log_executor = None


def audit_log_executor():
    global _audit_log_executor
    if _audit_log_executor is None:
        workers = max(1, int(getattr(settings, "AUDIT_LOG_WORKERS", 2)))
        _audit_log_executor = ThreadPoolExecutor(max_workers=workers, thread_name_prefix="audit-log")
    return _audit_log_executor


class User(AbstractUser):
    phone = models.CharField(max_length=32, blank=True)
    email = models.EmailField(unique=True)
    accepts_marketing = models.BooleanField(
        default=False,
        help_text="User opted in to deals, promo codes, and newsletter emails.",
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def clean(self):
        super().clean()
        errors = {}
        if not self.first_name.strip():
            errors["first_name"] = "First name is required."
        if not self.last_name.strip():
            errors["last_name"] = "Last name is required."
        if not re.fullmatch(r"^\+?\d{10,15}$", self.phone.strip()):
            errors["phone"] = "Phone number must be between 10 and 15 digits."
        if errors:
            raise ValidationError(errors)


class ActivityLog(models.Model):
    """Durable audit trail for business events worth searching later."""
    action = models.CharField(max_length=80)
    actor = models.CharField(max_length=200, blank=True, help_text="User email or 'system'.")
    message = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"], name="audit_created_idx"),
            models.Index(fields=["action", "-created_at"], name="audit_action_created_idx"),
            models.Index(fields=["actor", "-created_at"], name="audit_actor_created_idx"),
        ]

    def __str__(self):
        actor = self.actor or "system"
        return f"{self.action} by {actor} at {self.created_at:%Y-%m-%d %H:%M:%S}"

    @classmethod
    def log(cls, action, *, actor="", message="", metadata=None, async_=None):
        if not action:
            raise ValueError("ActivityLog action is required.")

        payload = {
            "action": action,
            "actor": actor or "system",
            "message": message or "",
            "metadata": metadata or {},
        }

        if async_ is None:
            async_ = getattr(settings, "AUDIT_LOG_ASYNC", True)

        if not async_:
            return cls._create_log(payload)

        future = audit_log_executor().submit(cls._create_log_in_thread, payload)
        future.add_done_callback(cls._handle_async_error)
        return future

    @classmethod
    def _create_log(cls, payload):
        return cls.objects.create(**payload)

    @classmethod
    def _create_log_in_thread(cls, payload):
        close_old_connections()
        try:
            return cls._create_log(payload)
        finally:
            close_old_connections()

    @staticmethod
    def _handle_async_error(future):
        exc = future.exception()
        if exc:
            logger.error("Failed to persist audit log.", exc_info=(type(exc), exc, exc.__traceback__))


class RateLimitBucket(models.Model):
    key = models.CharField(max_length=255, unique=True)
    count = models.PositiveIntegerField(default=0)
    expires_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["expires_at"], name="ratelimit_expires_idx"),
        ]

    def __str__(self):
        return f"{self.key} ({self.count})"


class Tour(models.Model):
    """Tour product type (Sunset Cruise, Dolphin Wildlife Excursion, etc.)."""
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=120)
    short_description = models.CharField(max_length=240)
    long_description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=120)
    price_per_person = models.PositiveIntegerField(default=60, help_text="USD per guest.")
    tax_rate_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Sales tax percentage for this tour. Example: 7.00 for 7%.",
    )
    min_party = models.PositiveSmallIntegerField(default=3)
    max_party = models.PositiveSmallIntegerField(default=6)
    image = models.ImageField(upload_to="tours/", blank=True, null=True,
                              help_text="Upload from your computer. Recommended 1600×1200.")
    image_url = models.CharField(max_length=500, blank=True,
                                 help_text="Optional fallback URL if no upload.")
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    # SEO
    seo_title = models.CharField(max_length=70, blank=True, help_text="Browser tab + Google. Best ≤60 chars.")
    seo_description = models.TextField(blank=True, help_text="Search description. Supports long copy up to about 2000 words.")
    seo_keywords = models.TextField(blank=True, help_text="Comma-separated keywords. Supports long lists up to about 2000 words.")
    og_image = models.ImageField(upload_to="tours/og/", blank=True, null=True,
                                 help_text="Social share preview. 1200×630.")

    class Meta:
        ordering = ["sort_order", "name"]
        indexes = [
            models.Index(fields=["is_active", "sort_order", "name"], name="tour_active_sort_idx"),
        ]

    def __str__(self):
        return self.name

    @property
    def image_src(self):
        if self.image:
            return self.image.url
        return self.image_url


class SiteImage(models.Model):
    """Reusable site images (hero, gallery, about). Edit via admin."""
    KEY_CHOICES = [
        ("logo", "Logo"),
        ("hero", "Homepage hero"),
        ("tours_hero", "Tours page hero"),
        ("contact_hero", "Contact page hero"),
        ("about", "About page banner"),
        ("about_secondary", "About secondary image"),
        ("story", "Story section background"),
        ("highlight_dolphin", "Highlight: dolphins"),
        ("highlight_manatee", "Highlight: manatees"),
        ("highlight_rocket", "Highlight: rocket"),
        ("gallery_1", "Gallery 1"), ("gallery_2", "Gallery 2"),
        ("gallery_3", "Gallery 3"), ("gallery_4", "Gallery 4"),
        ("gallery_5", "Gallery 5"), ("gallery_6", "Gallery 6"),
        ("gallery_7", "Gallery 7"), ("gallery_8", "Gallery 8"),
        ("og_default", "Default social share image"),
    ]
    key = models.CharField(max_length=40, choices=KEY_CHOICES, unique=True)
    image = models.ImageField(upload_to="site/", blank=True, null=True)
    default_path = models.CharField(
        max_length=240,
        blank=True,
        help_text="Fallback static path used until an uploaded replacement exists, e.g. /images/hero-ocean.jpg.",
    )
    alt_text = models.CharField(max_length=200, blank=True)
    caption = models.CharField(max_length=240, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_key_display()} ({self.image.name if self.image else self.default_path or 'not set'})"

    @property
    def image_src(self):
        if self.image:
            return self.image.url
        return self.default_path


class SiteSettings(models.Model):
    """Singleton: global SEO + contact info."""
    site_name = models.CharField(max_length=120, default="Dolphin Island Tours")
    tagline = models.CharField(max_length=240, default="Creating unforgettable dolphin encounters on Florida's Space Coast.")
    seo_title = models.CharField(max_length=70, default="Dolphin Island Tours | Merritt Island Dolphin & Sunset Boat Tours")
    seo_description = models.TextField(
        default="Book small-group dolphin, manatee, wildlife, sunset, and rocket launch boat tours from Merritt Island near Cocoa Beach and Cape Canaveral.")
    seo_keywords = models.TextField(
        default="Merritt Island dolphin tours, Cocoa Beach dolphin tour, Cape Canaveral boat tour, Space Coast wildlife tour, Indian River Lagoon tour, Florida sunset cruise")
    contact_email = models.EmailField(default="lauren@dolphinislandtours.com")
    contact_phone = models.CharField(max_length=40, blank=True, default="321-390-0176")
    address = models.CharField(max_length=240, default="2700 Harbor Town Drive, Merritt Island, FL 32952")
    meeting_instructions = models.CharField(
        max_length=240,
        default="Arrive 15 minutes before departure.",
        blank=True,
    )
    hours = models.CharField(max_length=120, default="Open daily 9 AM – 5 PM")
    maps_url = models.URLField(
        blank=True,
        default="https://maps.google.com/?q=2700+Harbor+Town+Drive+Merritt+Island+FL+32952",
    )
    map_embed_url = models.URLField(
        blank=True,
        default="https://www.google.com/maps?q=2700+Harbor+Town+Drive+Merritt+Island+FL+32952&output=embed",
    )
    price_blurb = models.CharField(max_length=160, default="$60 per person · 3–6 guests", blank=True)
    review_count = models.PositiveIntegerField(default=500)
    average_rating = models.DecimalField(max_digits=2, decimal_places=1, default=5.0)
    google_analytics_id = models.CharField(max_length=40, blank=True, help_text="e.g. G-XXXXXXXXXX")
    google_tag_manager_id = models.CharField(max_length=40, blank=True, help_text="e.g. GTM-XXXXXXX")
    google_ads_id = models.CharField(max_length=40, blank=True, help_text="e.g. AW-123456789")
    google_ads_booking_conversion_label = models.CharField(max_length=80, blank=True)
    meta_pixel_id = models.CharField(max_length=40, blank=True)
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    tiktok_url = models.URLField(blank=True)
    tripadvisor_url = models.URLField(blank=True)
    google_business_url = models.URLField(blank=True)
    google_review_url = models.URLField(
        blank=True,
        max_length=500,
        default="https://g.page/r/CehBxKNRm1TfEBM/review",
        help_text="Direct Google review/write-review link. Paste the Business Profile review link here if available.",
    )
    google_reviews_url = models.URLField(
        blank=True,
        max_length=500,
        default="https://share.google/Ig5FtVIQGXBWMUIGC",
        help_text="Public Google reviews link.",
    )
    google_reviews_embed_url = models.URLField(
        blank=True,
        max_length=500,
        default="https://www.google.com/maps?q=Dolphin+Island+Tours+LLC+2700+Harbortown+Dr+Merritt+Island+FL+32952&output=embed",
        help_text="Embeddable Google Maps/Business Profile URL shown on the reviews page.",
    )
    footer_legal_text = models.CharField(
        max_length=240,
        blank=True,
        default="Copyright © 2026 Dolphin Island Tours LLC | Licensed & Insured | USCG Certified Captain",
    )
    robots_txt = models.TextField(default="User-agent: *\nAllow: /\nSitemap: /sitemap.xml")

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self):
        return self.site_name

    @classmethod
    def get(cls):
        obj = cache.get(SITE_SETTINGS_CACHE_KEY)
        if obj is not None:
            return obj
        obj, _ = cls.objects.get_or_create(pk=1)
        cache.set(SITE_SETTINGS_CACHE_KEY, obj, getattr(settings, "SITE_CACHE_SECONDS", 300))
        return obj


class PageContent(models.Model):
    """Editable marketing copy for customer-facing pages."""
    PAGE_CHOICES = [
        ("home", "Home"),
        ("tours", "Tours listing"),
        ("book", "Booking"),
        ("reviews", "Reviews"),
        ("about", "About"),
        ("contact", "Contact"),
        ("find_booking", "Find booking"),
    ]
    page = models.CharField(max_length=32, choices=PAGE_CHOICES, unique=True)
    hero_image = models.ForeignKey(
        SiteImage,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="pages",
        help_text="Optional hero image slot. Upload/replace the image under Site images.",
    )
    seo_title = models.CharField(max_length=70, blank=True)
    seo_description = models.TextField(blank=True)
    seo_keywords = models.TextField(blank=True)
    hero_eyebrow = models.CharField(max_length=120, blank=True)
    hero_title = models.CharField(max_length=180, blank=True)
    hero_subtitle = models.TextField(blank=True)
    primary_button_label = models.CharField(max_length=80, blank=True)
    primary_button_url = models.CharField(max_length=200, blank=True)
    secondary_button_label = models.CharField(max_length=80, blank=True)
    secondary_button_url = models.CharField(max_length=200, blank=True)
    intro_eyebrow = models.CharField(max_length=120, blank=True)
    intro_title = models.CharField(max_length=180, blank=True)
    intro_body = models.TextField(blank=True)
    section_one_title = models.CharField(max_length=180, blank=True)
    section_one_body = models.TextField(blank=True)
    section_two_title = models.CharField(max_length=180, blank=True)
    section_two_body = models.TextField(blank=True)
    cta_title = models.CharField(max_length=180, blank=True)
    cta_body = models.TextField(blank=True)
    extra_content = models.JSONField(
        default=dict,
        blank=True,
        help_text="Optional structured content for cards/FAQs/testimonials. Leave as {} if not needed.",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["page"]
        verbose_name = "Page content"
        verbose_name_plural = "Page content"

    def __str__(self):
        return self.get_page_display()


class PageSection(models.Model):
    """Admin-managed content band for a specific page."""
    STYLE_CHOICES = [
        ("light", "Light"),
        ("ocean", "Ocean"),
        ("sunset", "Sunset / sale"),
        ("dark", "Dark"),
    ]
    page_content = models.ForeignKey(PageContent, on_delete=models.CASCADE, related_name="sections")
    title = models.CharField(max_length=160)
    eyebrow = models.CharField(max_length=80, blank=True)
    body = models.TextField(blank=True)
    image = models.ForeignKey(
        SiteImage,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="page_sections",
        help_text="Optional image shown beside the content.",
    )
    background_color = models.CharField(
        max_length=32,
        blank=True,
        help_text="Optional CSS color, e.g. #fff7ed. Leave blank to use the selected style.",
    )
    text_color = models.CharField(
        max_length=32,
        blank=True,
        help_text="Optional CSS color, e.g. #0b3a52. Leave blank to use the selected style.",
    )
    style = models.CharField(max_length=12, choices=STYLE_CHOICES, default="light")
    cta_label = models.CharField(max_length=80, blank=True)
    cta_url = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "id"]
        indexes = [
            models.Index(fields=["page_content", "is_active", "sort_order"], name="pagesection_page_active_idx"),
        ]

    def __str__(self):
        return f"{self.page_content}: {self.title}"


class NavigationLink(models.Model):
    """Editable global header/footer link."""
    AREA_CHOICES = [
        ("header", "Header"),
        ("footer", "Footer"),
    ]
    VISIBILITY_CHOICES = [
        ("all", "Everyone"),
        ("anonymous", "Logged-out users"),
        ("authenticated", "Logged-in users"),
    ]
    area = models.CharField(max_length=12, choices=AREA_CHOICES, default="header")
    label = models.CharField(max_length=80)
    url = models.CharField(max_length=200)
    visibility = models.CharField(max_length=16, choices=VISIBILITY_CHOICES, default="all")
    is_button = models.BooleanField(default=False, help_text="Use primary button styling in the header.")
    opens_new_tab = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["area", "sort_order", "id"]
        indexes = [
            models.Index(fields=["area", "is_active", "sort_order"], name="navlink_area_active_idx"),
        ]

    def __str__(self):
        return f"{self.get_area_display()}: {self.label}"


class FAQItem(models.Model):
    """Editable homepage FAQ item."""
    question = models.CharField(max_length=220)
    answer = models.TextField()
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "FAQ item"
        verbose_name_plural = "FAQ items"
        indexes = [
            models.Index(fields=["is_active", "sort_order"], name="faq_active_sort_idx"),
        ]

    def __str__(self):
        return self.question


class ContactMessage(models.Model):
    """Visitor query/contact form submission."""
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    handled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        label = self.subject or (self.created_at.strftime("%Y-%m-%d") if self.created_at else "unsaved")
        return f"{self.name} <{self.email}> – {label}"


class EmailDeliveryJob(models.Model):
    STATUS = [
        ("queued", "Queued"),
        ("sending", "Sending"),
        ("sent", "Sent"),
        ("failed", "Failed"),
    ]
    name = models.CharField(max_length=200)
    source = models.CharField(max_length=80, blank=True)
    campaign = models.ForeignKey(
        "EmailCampaign",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="delivery_jobs",
    )
    status = models.CharField(max_length=10, choices=STATUS, default="queued")
    total_count = models.PositiveIntegerField(default=0)
    sent_count = models.PositiveIntegerField(default=0)
    failed_count = models.PositiveIntegerField(default=0)
    created_by = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(blank=True, null=True)
    finished_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"], name="emailjob_status_created_idx"),
            models.Index(fields=["campaign", "-created_at"], name="emailjob_campaign_idx"),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

    def refresh_stats(self, save=True):
        from django.db.models import Count, Q
        from django.utils import timezone as tz

        stats = self.recipients.aggregate(
            total=Count("id"),
            sent=Count("id", filter=Q(status="sent")),
            failed=Count("id", filter=Q(status="failed")),
        )
        self.total_count = stats["total"] or 0
        self.sent_count = stats["sent"] or 0
        self.failed_count = stats["failed"] or 0
        done_count = self.sent_count + self.failed_count
        if self.total_count and done_count >= self.total_count:
            self.status = "failed" if self.sent_count == 0 else "sent"
            if not self.finished_at:
                self.finished_at = tz.now()
        elif self.status != "sending":
            self.status = "queued"
        if save:
            self.save(update_fields=["total_count", "sent_count", "failed_count", "status", "finished_at"])
        return self


class EmailDeliveryRecipient(models.Model):
    STATUS = [
        ("pending", "Pending"),
        ("sending", "Sending"),
        ("sent", "Sent"),
        ("failed", "Failed"),
    ]
    job = models.ForeignKey(EmailDeliveryJob, on_delete=models.CASCADE, related_name="recipients")
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    html = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS, default="pending")
    promo_code = models.ForeignKey("PromoCode", on_delete=models.SET_NULL, null=True, blank=True)
    attempts = models.PositiveSmallIntegerField(default=0)
    last_error = models.TextField(blank=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]
        indexes = [
            models.Index(fields=["status", "created_at"], name="emailrecip_status_created_idx"),
            models.Index(fields=["job", "status"], name="emailrecip_job_status_idx"),
            models.Index(fields=["email"], name="emailrecip_email_idx"),
        ]

    def __str__(self):
        return f"{self.email} ({self.get_status_display()})"


class TourSlot(models.Model):
    """Available departure date/time. Admin manages these."""
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name="slots")
    date = models.DateField()
    time = models.TimeField()
    capacity = models.PositiveSmallIntegerField(default=6)
    is_active = models.BooleanField(default=True)
    notes = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ("tour", "date", "time")
        ordering = ["date", "time"]
        indexes = [
            models.Index(fields=["tour", "is_active", "date", "time"], name="slot_tour_act_date_idx"),
            models.Index(fields=["is_active", "date", "time"], name="slot_act_date_idx"),
        ]

    def __str__(self):
        return f"{self.tour.name} – {self.date} {self.time} (cap {self.capacity})"

    @property
    def seats_booked(self):
        if hasattr(self, "booked_seats"):
            return self.booked_seats or 0
        return sum(b.party_size for b in self.bookings.filter(status__in=["paid", "pending"]))

    @property
    def seats_remaining(self):
        return max(0, self.capacity - self.seats_booked)


class Booking(models.Model):
    STATUS = [
        ("pending", "Pending Payment"),
        ("paid", "Paid"),
        ("payment_failed", "Payment Failed"),
        ("expired", "Expired Hold"),
        ("cancelled", "Cancelled"),
        ("refunded", "Refunded"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="bookings")
    slot = models.ForeignKey(TourSlot, on_delete=models.PROTECT, related_name="bookings")
    party_size = models.PositiveSmallIntegerField()
    price_per_person_cents = models.PositiveIntegerField()
    tax_cents = models.PositiveIntegerField(default=0)
    total_cents = models.PositiveIntegerField()
    status = models.CharField(max_length=16, choices=STATUS, default="pending")
    square_payment_id = models.CharField(max_length=128, blank=True)
    square_order_id = models.CharField(max_length=128, blank=True)
    customer_first_name = models.CharField(max_length=60, blank=True)
    customer_last_name = models.CharField(max_length=60, blank=True)
    customer_name = models.CharField(max_length=120)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=32, blank=True)
    travelers = models.JSONField(default=list, blank=True)
    special_requests = models.TextField(blank=True)
    promo_code = models.ForeignKey("PromoCode", on_delete=models.SET_NULL, null=True, blank=True, related_name="bookings")
    discount_cents = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slot", "status"], name="booking_slot_status_idx"),
            models.Index(fields=["user", "-created_at"], name="booking_user_created_idx"),
            models.Index(fields=["customer_email", "-created_at"], name="booking_email_created_idx"),
        ]

    def __str__(self):
        return f"{self.customer_name} – {self.slot} – {self.status}"


class DeletedBookingReport(models.Model):
    """Snapshot kept for reports after a booking row is deleted."""
    booking_id = models.UUIDField(unique=True)
    user_email = models.EmailField(blank=True)
    customer_name = models.CharField(max_length=120)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=32, blank=True)
    tour_name = models.CharField(max_length=120, blank=True)
    tour_date = models.DateField(blank=True, null=True)
    tour_time = models.TimeField(blank=True, null=True)
    party_size = models.PositiveSmallIntegerField()
    status = models.CharField(max_length=16)
    price_per_person_cents = models.PositiveIntegerField()
    discount_cents = models.PositiveIntegerField(default=0)
    tax_cents = models.PositiveIntegerField(default=0)
    total_cents = models.PositiveIntegerField()
    square_payment_id = models.CharField(max_length=128, blank=True)
    square_order_id = models.CharField(max_length=128, blank=True)
    promo_code_text = models.CharField(max_length=40, blank=True)
    travelers = models.JSONField(default=list, blank=True)
    special_requests = models.TextField(blank=True)
    original_created_at = models.DateTimeField()
    original_updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(auto_now_add=True)
    deleted_by = models.EmailField(blank=True)

    class Meta:
        ordering = ["-original_created_at"]
        indexes = [
            models.Index(fields=["-original_created_at"], name="delbook_created_idx"),
            models.Index(fields=["status", "-original_created_at"], name="delbook_status_created_idx"),
            models.Index(fields=["customer_email", "-original_created_at"], name="delbook_email_created_idx"),
        ]

    def __str__(self):
        return f"Deleted booking {self.booking_id} – {self.customer_email}"


def archive_booking_for_report(booking, deleted_by=""):
    """Persist a booking snapshot before deletion so reports keep transaction history."""
    existing = DeletedBookingReport.objects.filter(booking_id=booking.id).first()
    if existing:
        if deleted_by and not existing.deleted_by:
            existing.deleted_by = deleted_by
            existing.save(update_fields=["deleted_by"])
        return existing, False
    return DeletedBookingReport.objects.create(
        booking_id=booking.id,
        user_email=booking.user.email if booking.user_id else "",
        customer_name=booking.customer_name,
        customer_email=booking.customer_email,
        customer_phone=booking.customer_phone,
        tour_name=booking.slot.tour.name if booking.slot_id else "",
        tour_date=booking.slot.date if booking.slot_id else None,
        tour_time=booking.slot.time if booking.slot_id else None,
        party_size=booking.party_size,
        status=booking.status,
        price_per_person_cents=booking.price_per_person_cents,
        discount_cents=booking.discount_cents,
        tax_cents=booking.tax_cents,
        total_cents=booking.total_cents,
        square_payment_id=booking.square_payment_id,
        square_order_id=booking.square_order_id,
        promo_code_text=booking.promo_code.code if booking.promo_code_id else "",
        travelers=booking.travelers,
        special_requests=booking.special_requests,
        original_created_at=booking.created_at,
        original_updated_at=booking.updated_at,
        deleted_by=deleted_by or "",
    ), True


@receiver(pre_delete, sender=Booking)
def archive_booking_on_delete(sender, instance, **kwargs):
    archive_booking_for_report(instance)


class Review(models.Model):
    """Customer review with star rating. Admin-moderated."""
    tour = models.ForeignKey(Tour, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviews")
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviews")
    author_name = models.CharField(max_length=120)
    author_email = models.EmailField(blank=True)
    rating = models.PositiveSmallIntegerField(default=5, help_text="1–5 stars")
    title = models.CharField(max_length=160, blank=True)
    body = models.TextField()
    photo = models.ImageField(upload_to="reviews/", blank=True, null=True)
    reply_text = models.TextField(blank=True, help_text="Public owner reply shown below the review.")
    helpful_count = models.PositiveIntegerField(default=0)
    is_approved = models.BooleanField(default=False, help_text="Hidden from site until approved.")
    is_featured = models.BooleanField(default=False, help_text="Show on homepage testimonials.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tour", "is_approved", "is_featured", "-created_at"], name="review_tour_state_idx"),
            models.Index(fields=["user", "tour"], name="review_user_tour_idx"),
            models.Index(fields=["tour", "author_email"], name="review_tour_email_idx"),
        ]

    def __str__(self):
        return f"{self.author_name} – {self.rating}★ – {self.tour or 'general'}"


class ReviewPhoto(models.Model):
    """Additional customer photos attached to a review."""
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="reviews/")
    sort_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"Photo {self.id} for review {self.review_id}"


class ReviewHelpfulVote(models.Model):
    """One helpful vote per authenticated user or browser session."""
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="helpful_votes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name="review_helpful_votes")
    session_key = models.CharField(max_length=40, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["review", "user"], name="review_vote_user_idx"),
            models.Index(fields=["review", "session_key"], name="review_vote_session_idx"),
        ]

    def __str__(self):
        voter = self.user_id or self.session_key or "anonymous"
        return f"Helpful vote for review {self.review_id} by {voter}"


class MailingListEntry(models.Model):
    """Extra emails (non-users) for campaigns. Add manually in admin."""
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=120, blank=True)
    tags = models.CharField(max_length=240, blank=True, help_text="Comma-separated, e.g. vip,2024-guest")
    subscribed = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["subscribed", "-created_at"], name="mailing_sub_created_idx"),
        ]
        verbose_name_plural = "Mailing list entries"

    def __str__(self):
        return self.email


class PromoCode(models.Model):
    KIND = [("percent", "Percent off"), ("amount", "Amount off ($)")]
    code = models.CharField(max_length=40, unique=True)
    label = models.CharField(max_length=120, blank=True, help_text="Internal name, e.g. 'Summer 10% blast'")
    kind = models.CharField(max_length=10, choices=KIND, default="percent")
    percent_off = models.PositiveSmallIntegerField(
        default=10,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Used when kind=percent. 1–100.",
    )
    amount_off_cents = models.PositiveIntegerField(default=0, help_text="Used when kind=amount. Cents.")
    max_uses = models.PositiveIntegerField(default=1, help_text="0 = unlimited.")
    used_count = models.PositiveIntegerField(default=0)
    locked_to_email = models.EmailField(blank=True, help_text="Optional: only this email can redeem.")
    expires_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    campaign = models.ForeignKey("EmailCampaign", on_delete=models.SET_NULL, null=True, blank=True, related_name="codes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_active", "expires_at"], name="promo_active_exp_idx"),
            models.Index(fields=["locked_to_email"], name="promo_locked_email_idx"),
        ]

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        # Codes are matched case-insensitively; storing them upper-cased keeps
        # the unique constraint from allowing "SAVE10" and "save10" to coexist.
        if self.code:
            self.code = self.code.strip().upper()
        super().save(*args, **kwargs)

    def is_redeemable(self, email=None):
        from django.utils import timezone as tz
        if not self.is_active:
            return False, "Code is inactive."
        if self.expires_at and self.expires_at < tz.now():
            return False, "Code has expired."
        if self.max_uses and self.used_count >= self.max_uses:
            return False, "Code has been fully redeemed."
        if self.locked_to_email:
            if not email:
                return False, "Email is required for this code."
            if self.locked_to_email.lower() != email.lower():
                return False, "This code is for a different email."
        return True, ""

    def discount_for(self, subtotal_cents):
        if self.kind == "percent":
            return subtotal_cents * self.percent_off // 100
        return min(self.amount_off_cents, subtotal_cents)


class EmailCampaign(models.Model):
    STATUS = [("draft", "Draft"), ("sending", "Sending"), ("sent", "Sent"), ("failed", "Failed")]
    AUDIENCE = [
        ("all_users", "All registered users"),
        ("subscribed_users", "Subscribed mailing list only"),
        ("both", "Users + mailing list"),
        ("manual", "Manual emails only (paste below)"),
    ]
    name = models.CharField(max_length=120, help_text="Internal name.")
    subject = models.CharField(max_length=200)
    body = models.TextField(help_text="Plain text or HTML. Variables: {name}, {promo_code}.")
    audience = models.CharField(max_length=20, choices=AUDIENCE, default="all_users")
    manual_emails = models.TextField(blank=True, help_text="One email per line. Used with 'manual' or added to other audiences.")
    cta_label = models.CharField(max_length=80, blank=True)
    cta_url = models.CharField(max_length=400, blank=True)
    # promo
    attach_promo = models.BooleanField(default=False, help_text="Generate a unique promo code per recipient.")
    promo_kind = models.CharField(max_length=10, choices=PromoCode.KIND, default="percent")
    promo_percent_off = models.PositiveSmallIntegerField(default=10)
    promo_amount_off_cents = models.PositiveIntegerField(default=0)
    promo_expires_at = models.DateTimeField(blank=True, null=True)
    # state
    status = models.CharField(max_length=10, choices=STATUS, default="draft")
    sent_count = models.PositiveIntegerField(default=0)
    failed_count = models.PositiveIntegerField(default=0)
    last_run_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

    def collect_recipients(self):
        """Return list of (email, name) tuples, deduped."""
        out = {}
        from django.contrib.auth import get_user_model
        U = get_user_model()
        if self.audience in ("all_users", "both"):
            users = (
                U.objects.exclude(email="")
                .filter(accepts_marketing=True)
                .annotate(email_key=Lower("email"))
                .values_list("email_key", "email", "first_name", "last_name", "username")
                .order_by("email_key")
                .iterator(chunk_size=2000)
            )
            for email_key, email, first_name, last_name, username in users:
                name = f"{first_name} {last_name}".strip() or username
                out.setdefault(email_key, (email, name))
        if self.audience in ("subscribed_users", "both"):
            entries = (
                MailingListEntry.objects.filter(subscribed=True)
                .annotate(email_key=Lower("email"))
                .values_list("email_key", "email", "name")
                .order_by("email_key")
                .iterator(chunk_size=2000)
            )
            for email_key, email, name in entries:
                out.setdefault(email_key, (email, name or ""))
        if self.manual_emails:
            for line in self.manual_emails.splitlines():
                addr = line.strip()
                if "@" in addr:
                    out.setdefault(addr.lower(), (addr, ""))
        return list(out.values())


def invalidate_site_cache(**kwargs):
    cache.delete_many([SITE_SETTINGS_CACHE_KEY, SITE_PAYLOAD_CACHE_KEY])


def invalidate_review_stats_cache(instance, **kwargs):
    cache.delete(ALL_REVIEW_STATS_CACHE_KEY)
    if instance.tour_id:
        cache.delete(f"{REVIEW_STATS_CACHE_PREFIX}{instance.tour_id}")


post_save.connect(invalidate_site_cache, sender=SiteSettings)
post_delete.connect(invalidate_site_cache, sender=SiteSettings)
post_save.connect(invalidate_site_cache, sender=SiteImage)
post_delete.connect(invalidate_site_cache, sender=SiteImage)
post_save.connect(invalidate_site_cache, sender=PageContent)
post_delete.connect(invalidate_site_cache, sender=PageContent)
post_save.connect(invalidate_site_cache, sender=PageSection)
post_delete.connect(invalidate_site_cache, sender=PageSection)
post_save.connect(invalidate_site_cache, sender=NavigationLink)
post_delete.connect(invalidate_site_cache, sender=NavigationLink)
post_save.connect(invalidate_site_cache, sender=FAQItem)
post_delete.connect(invalidate_site_cache, sender=FAQItem)
post_save.connect(invalidate_review_stats_cache, sender=Review)
post_delete.connect(invalidate_review_stats_cache, sender=Review)


@receiver(post_save, sender=User)
def sync_mailing_list_entry(sender, instance, **kwargs):
    if instance.accepts_marketing:
        name = f"{instance.first_name} {instance.last_name}".strip() or instance.username
        entry, created = MailingListEntry.objects.get_or_create(
            email__iexact=instance.email,
            defaults={"email": instance.email, "name": name, "subscribed": True}
        )
        if not created and not entry.subscribed:
            entry.subscribed = True
            if name and not entry.name:
                entry.name = name
            entry.save(update_fields=["subscribed", "name"])
    else:
        MailingListEntry.objects.filter(email__iexact=instance.email).update(subscribed=False)
