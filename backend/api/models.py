from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.exceptions import ValidationError
import uuid
import re


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
        if not re.fullmatch(r"\d{10}", self.phone.strip()):
            errors["phone"] = "Phone number must be exactly 10 digits."
        if errors:
            raise ValidationError(errors)


class Tour(models.Model):
    """Tour product type (Sunset Cruise, Dolphin Wildlife Excursion, etc.)."""
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=120)
    short_description = models.CharField(max_length=240)
    long_description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=120)
    price_per_person = models.PositiveIntegerField(default=60, help_text="USD per guest.")
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
    seo_description = models.CharField(max_length=180, blank=True, help_text="Google snippet. Best 140–160 chars.")
    seo_keywords = models.CharField(max_length=240, blank=True, help_text="Comma-separated.")
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
    tagline = models.CharField(max_length=240, default="Small-group dolphin, wildlife, sunset, and rocket-launch boat tours on Florida's Space Coast.")
    seo_title = models.CharField(max_length=70, default="Dolphin Island Tours | Merritt Island Dolphin & Sunset Boat Tours")
    seo_description = models.CharField(max_length=180,
        default="Book small-group dolphin, manatee, wildlife, sunset, and rocket launch boat tours from Merritt Island near Cocoa Beach and Cape Canaveral.")
    seo_keywords = models.CharField(max_length=240,
        default="Merritt Island dolphin tours, Cocoa Beach dolphin tour, Cape Canaveral boat tour, Space Coast wildlife tour, Indian River Lagoon tour, Florida sunset cruise")
    contact_email = models.EmailField(default="lewis@dolphinislandtours.com")
    contact_phone = models.CharField(max_length=40, blank=True)
    address = models.CharField(max_length=240, default="2700 Harbortown Drive, Merritt Island, FL")
    meeting_instructions = models.CharField(
        max_length=240,
        default="Arrive 15 minutes before departure.",
        blank=True,
    )
    hours = models.CharField(max_length=120, default="Open daily 9 AM – 5 PM")
    maps_url = models.URLField(
        blank=True,
        default="https://maps.google.com/?q=2700+Harbortown+Drive+Merritt+Island+FL",
    )
    map_embed_url = models.URLField(
        blank=True,
        default="https://www.google.com/maps?q=2700+Harbortown+Drive+Merritt+Island+FL&output=embed",
    )
    price_blurb = models.CharField(max_length=160, default="$60 per person · 3–6 guests", blank=True)
    tax_rate_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Sales tax percentage added at checkout. Example: 7.00 for 7%.",
    )
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
    robots_txt = models.TextField(default="User-agent: *\nAllow: /\nSitemap: /sitemap.xml")

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self):
        return self.site_name

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class PageContent(models.Model):
    """Editable marketing copy for customer-facing pages."""
    PAGE_CHOICES = [
        ("home", "Home"),
        ("tours", "Tours listing"),
        ("about", "About"),
        ("contact", "Contact"),
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
    seo_description = models.CharField(max_length=180, blank=True)
    seo_keywords = models.CharField(max_length=240, blank=True)
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


class ActivityLog(models.Model):
    """Audit log for important system events."""
    LEVELS = [("info", "Info"), ("warn", "Warning"), ("error", "Error"), ("success", "Success")]
    level = models.CharField(max_length=10, choices=LEVELS, default="info")
    action = models.CharField(max_length=80)
    actor = models.CharField(max_length=200, blank=True, help_text="User email or 'system'")
    message = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.level}] {self.action} – {self.created_at:%Y-%m-%d %H:%M}"

    @classmethod
    def log(cls, action, message="", level="info", actor="system", **metadata):
        return cls.objects.create(action=action, message=message, level=level, actor=actor, metadata=metadata)


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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    slot = models.ForeignKey(TourSlot, on_delete=models.PROTECT, related_name="bookings")
    party_size = models.PositiveSmallIntegerField()
    price_per_person_cents = models.PositiveIntegerField()
    tax_cents = models.PositiveIntegerField(default=0)
    total_cents = models.PositiveIntegerField()
    status = models.CharField(max_length=16, choices=STATUS, default="pending")
    square_payment_id = models.CharField(max_length=128, blank=True)
    square_order_id = models.CharField(max_length=128, blank=True)
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
    percent_off = models.PositiveSmallIntegerField(default=10, help_text="Used when kind=percent. 1–100.")
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
            for u in U.objects.exclude(email="").filter(accepts_marketing=True):
                out.setdefault(u.email.lower(), (u.email, (f"{u.first_name} {u.last_name}".strip() or u.username)))
        if self.audience in ("subscribed_users", "both"):
            for e in MailingListEntry.objects.filter(subscribed=True):
                out.setdefault(e.email.lower(), (e.email, e.name or ""))
        if self.manual_emails:
            for line in self.manual_emails.splitlines():
                addr = line.strip()
                if "@" in addr:
                    out.setdefault(addr.lower(), (addr, ""))
        return list(out.values())
