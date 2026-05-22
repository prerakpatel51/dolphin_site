from django.contrib import admin, messages
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.shortcuts import render, redirect
from django.urls import path, reverse
from django import forms
from django.utils import timezone
from datetime import timedelta, datetime
from django.utils.html import format_html, format_html_join
from .models import (User, Tour, TourSlot, Booking, SiteImage, SiteSettings, ContactMessage,
                     ActivityLog, PageContent, PromoCode, MailingListEntry, EmailCampaign)
import secrets, string


class BulkSlotForm(forms.Form):
    tour = forms.ModelChoiceField(queryset=Tour.objects.all())
    start_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    times = forms.CharField(help_text="Comma-separated, 24h. e.g. 09:00,12:00,15:00,18:00",
                            initial="09:00,12:00,15:00,18:00")
    capacity = forms.IntegerField(min_value=1, max_value=20, initial=6)
    weekdays = forms.MultipleChoiceField(
        choices=[(str(i), d) for i, d in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])],
        widget=forms.CheckboxSelectMultiple,
        initial=["0", "1", "2", "3", "4", "5", "6"],
    )


class ContactReplyForm(forms.Form):
    subject = forms.CharField(max_length=200)
    message = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 10, "style": "width: min(760px, 100%);"}),
        help_text="This will be emailed directly to the visitor.",
    )


class PromotionalEmailForm(forms.Form):
    subject = forms.CharField(max_length=200)
    message = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 12, "style": "width: min(820px, 100%);"}),
        help_text="Use this for announcements, deals, and promotional updates.",
    )
    cta_label = forms.CharField(
        label="Button label",
        max_length=80,
        required=False,
        initial="Book now",
        help_text="Optional call-to-action button text.",
    )
    cta_url = forms.URLField(
        label="Button URL",
        required=False,
        help_text="Optional URL for the button, e.g. https://dolphinislandtours.com/tours",
    )
    extra_emails = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 5, "style": "width: min(820px, 100%);"}),
        help_text="Optional extra recipients. Separate emails with commas, spaces, or new lines.",
    )
    attach_promo = forms.BooleanField(
        required=False,
        label="Attach unique promo code per recipient",
        help_text="Generates a single-use code per email, locked to that address. Use {promo_code} in the message to insert it inline; otherwise it appears in a badge below the body.",
    )
    promo_kind = forms.ChoiceField(
        required=False,
        choices=[("percent", "Percent off"), ("amount", "Amount off ($)")],
        initial="percent",
    )
    promo_percent_off = forms.IntegerField(
        required=False, initial=10, min_value=1, max_value=100,
        help_text="Used when kind = percent.",
    )
    promo_amount_off_cents = forms.IntegerField(
        required=False, initial=0, min_value=0,
        help_text="Used when kind = amount. In cents (e.g. 1500 = $15).",
    )
    promo_expires_at = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        help_text="Optional. Leave blank for no expiry.",
    )

    def clean_extra_emails(self):
        import re
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError

        raw = self.cleaned_data.get("extra_emails", "")
        emails = [e.strip() for e in re.split(r"[\s,;]+", raw) if e.strip()]
        invalid = []
        for email in emails:
            try:
                validate_email(email)
            except ValidationError:
                invalid.append(email)
        if invalid:
            raise forms.ValidationError(f"Invalid email address(es): {', '.join(invalid)}")
        return emails


def selected_action_inputs(request):
    return request.POST.getlist(ACTION_CHECKBOX_NAME)


def promotional_email_recipients(queryset, email_getter, extra_emails):
    recipients = []
    seen = set()
    for obj in queryset:
        email = (email_getter(obj) or "").strip().lower()
        if email and email not in seen:
            recipients.append(email)
            seen.add(email)
    for email in extra_emails:
        normalized = email.strip().lower()
        if normalized and normalized not in seen:
            recipients.append(normalized)
            seen.add(normalized)
    return recipients


def send_promotional_email_action(modeladmin, request, queryset, source_label, email_getter):
    if "apply" in request.POST:
        form = PromotionalEmailForm(request.POST)
        if form.is_valid():
            from .emails import send_email, promotional_email_html, campaign_email_html

            recipients = promotional_email_recipients(
                queryset,
                email_getter,
                form.cleaned_data["extra_emails"],
            )
            if not recipients:
                modeladmin.message_user(request, "No valid email recipients found.", level=messages.WARNING)
                return None

            subject = form.cleaned_data["subject"]
            attach_promo = form.cleaned_data.get("attach_promo")
            promo_codes_made = []
            sent = 0
            failed = []
            for email in recipients:
                promo_code = ""
                if attach_promo:
                    pc = PromoCode.objects.create(
                        code=_gen_promo_code(prefix="PROMO"),
                        label=f"Bulk email · {subject[:60]}",
                        kind=form.cleaned_data.get("promo_kind") or "percent",
                        percent_off=form.cleaned_data.get("promo_percent_off") or 10,
                        amount_off_cents=form.cleaned_data.get("promo_amount_off_cents") or 0,
                        max_uses=1,
                        locked_to_email=email,
                        expires_at=form.cleaned_data.get("promo_expires_at"),
                    )
                    promo_code = pc.code
                    promo_codes_made.append(pc.code)
                # If promo attached, use campaign_email_html so {promo_code}/{name} fill in and badge shows.
                if attach_promo:
                    html = campaign_email_html(
                        form.cleaned_data["message"],
                        name="", promo_code=promo_code,
                        cta_label=form.cleaned_data["cta_label"],
                        cta_url=form.cleaned_data["cta_url"],
                    )
                else:
                    html = promotional_email_html(
                        form.cleaned_data["message"],
                        form.cleaned_data["cta_label"],
                        form.cleaned_data["cta_url"],
                    )
                try:
                    send_email(email, subject, html)
                    sent += 1
                except Exception as e:
                    failed.append(f"{email}: {e}")

            ActivityLog.log(
                "marketing.bulk_email_sent",
                f"{sent} sent, {len(failed)} failed from {source_label}"
                + (f", {len(promo_codes_made)} promo codes" if promo_codes_made else ""),
                level="success" if not failed else "warn",
                actor=request.user.email,
                subject=subject,
                recipients=recipients,
                failures=failed[:20],
                promo_codes=promo_codes_made[:50],
            )
            if failed:
                modeladmin.message_user(
                    request,
                    f"Sent {sent} promotional emails. {len(failed)} failed; see Activity logs.",
                    level=messages.WARNING,
                )
            else:
                modeladmin.message_user(request, f"Sent {sent} promotional emails.", level=messages.SUCCESS)
            return None
    else:
        form = PromotionalEmailForm(initial={
            "subject": "Special offer from Dolphin Island Tours",
            "message": "Hi,\n\nWe have a new Dolphin Island Tours update for you.\n\n",
        })

    selected = selected_action_inputs(request)
    return render(request, "admin/bulk_promotional_email.html", {
        "title": "Send promotional email",
        "form": form,
        "queryset": queryset,
        "selected": selected,
        "action_name": request.POST.get("action"),
        "select_across": request.POST.get("select_across", "0"),
        "source_label": source_label,
        "recipient_count": queryset.count(),
    })


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ("preview", "name", "slug", "duration_minutes", "price_per_person", "min_party", "max_party", "is_active", "sort_order")
    list_display_links = ("preview", "name")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("is_active", "sort_order")
    fieldsets = (
        ("Basics", {"fields": ("name", "slug", "short_description", "long_description",
                               "duration_minutes", "price_per_person", "min_party",
                               "max_party", "is_active", "sort_order")}),
        ("Image", {"fields": ("image", "image_url"),
                   "description": "Upload an image OR paste an external URL. Upload wins."}),
        ("SEO", {"fields": ("seo_title", "seo_description", "seo_keywords", "og_image"),
                 "classes": ("collapse",),
                 "description": "Custom search/social metadata for this tour."}),
    )

    def preview(self, obj):
        src = obj.image.url if obj.image else obj.image_url
        if src:
            return format_html('<img src="{}" style="height:50px;border-radius:6px;object-fit:cover" />', src)
        return "—"
    preview.short_description = "Image"


@admin.register(SiteImage)
class SiteImageAdmin(admin.ModelAdmin):
    list_display = ("preview", "key", "current_source", "alt_text", "updated_at")
    list_display_links = ("preview", "key")
    list_filter = ("key",)
    search_fields = ("key", "alt_text", "caption")
    readonly_fields = ("large_preview",)
    fieldsets = (
        ("Image slot", {"fields": ("key", "large_preview", "image", "default_path")}),
        ("Metadata", {"fields": ("alt_text", "caption")}),
    )

    def preview(self, obj):
        if obj.image_src:
            return format_html('<img src="{}" style="height:60px;width:90px;border-radius:6px;object-fit:cover" />', obj.image_src)
        return "—"
    preview.short_description = "Preview"

    def large_preview(self, obj):
        if obj and obj.image_src:
            return format_html('<img src="{}" style="max-width:520px;max-height:260px;border-radius:8px;object-fit:cover;border:1px solid #ddd" />', obj.image_src)
        return "No image selected yet."
    large_preview.short_description = "Current image"

    def current_source(self, obj):
        return "Uploaded" if obj.image else (obj.default_path or "—")
    current_source.short_description = "Source"


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Site identity", {"fields": ("site_name", "tagline")}),
        ("SEO", {"fields": ("seo_title", "seo_description", "seo_keywords")}),
        ("Contact info", {"fields": ("contact_email", "contact_phone", "address",
                                     "meeting_instructions", "hours", "maps_url", "map_embed_url")}),
        ("Booking display", {"fields": ("price_blurb", "tax_rate_percent", "review_count", "average_rating")}),
        ("Analytics & ads", {"fields": ("google_analytics_id", "google_tag_manager_id",
                                        "google_ads_id", "google_ads_booking_conversion_label",
                                        "meta_pixel_id"),
                             "classes": ("collapse",)}),
        ("Social links", {"fields": ("facebook_url", "instagram_url", "youtube_url",
                                     "tiktok_url", "tripadvisor_url", "google_business_url")}),
        ("Robots.txt", {"fields": ("robots_txt",), "classes": ("collapse",)}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PageContent)
class PageContentAdmin(admin.ModelAdmin):
    list_display = ("page", "hero_title", "hero_image_preview", "updated_at")
    list_display_links = ("page", "hero_title")
    search_fields = ("page", "hero_title", "hero_subtitle", "intro_title",
                     "intro_body", "section_one_title", "section_one_body")
    readonly_fields = ("hero_image_preview",)
    fieldsets = (
        ("Page", {"fields": ("page", "hero_image", "hero_image_preview")}),
        ("SEO", {"fields": ("seo_title", "seo_description", "seo_keywords"), "classes": ("collapse",)}),
        ("Hero", {"fields": ("hero_eyebrow", "hero_title", "hero_subtitle",
                             "primary_button_label", "primary_button_url",
                             "secondary_button_label", "secondary_button_url")}),
        ("Main content", {"fields": ("intro_eyebrow", "intro_title", "intro_body",
                                     "section_one_title", "section_one_body",
                                     "section_two_title", "section_two_body")}),
        ("Call to action / success copy", {"fields": ("cta_title", "cta_body")}),
        ("Advanced structured content", {"fields": ("extra_content",),
                                         "classes": ("collapse",),
                                         "description": "Optional JSON for cards, FAQs, reviews, or future sections."}),
    )

    def hero_image_preview(self, obj):
        if obj and obj.hero_image and obj.hero_image.image_src:
            return format_html('<img src="{}" style="height:70px;width:120px;border-radius:6px;object-fit:cover" />',
                               obj.hero_image.image_src)
        return "—"
    hero_image_preview.short_description = "Hero image preview"


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("created_at", "name", "email", "subject", "handled", "reply_link")
    list_filter = ("handled", "created_at")
    list_editable = ("handled",)
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("name", "email", "phone", "subject", "message", "created_at", "reply_link")
    actions = ["send_promotional_email"]

    def get_urls(self):
        urls = super().get_urls()
        return [path("<int:message_id>/reply/", self.admin_site.admin_view(self.reply_view),
                     name="contactmessage-reply")] + urls

    def reply_link(self, obj):
        if not obj or not obj.pk:
            return "—"
        return format_html(
            '<a class="button" style="background:#0b6a8a;color:#fff;padding:3px 10px;border-radius:4px;text-decoration:none" href="{}">Reply by email</a>',
            reverse("admin:contactmessage-reply", args=[obj.pk]),
        )
    reply_link.short_description = "Reply"

    def reply_view(self, request, message_id):
        msg = ContactMessage.objects.get(pk=message_id)
        default_subject = f"Re: {msg.subject}" if msg.subject else "Re: Your Dolphin Island Tours message"

        if request.method == "POST":
            form = ContactReplyForm(request.POST)
            if form.is_valid():
                from .emails import send_email, contact_reply_html
                subject = form.cleaned_data["subject"]
                body = form.cleaned_data["message"]
                try:
                    send_email(msg.email, subject, contact_reply_html(msg, body))
                    msg.handled = True
                    msg.save(update_fields=["handled"])
                    ActivityLog.log("contact.reply_sent", f"Reply sent to {msg.email}",
                                    level="success", actor=request.user.email,
                                    contact_message_id=msg.id, subject=subject)
                    messages.success(request, f"Reply sent to {msg.email}.")
                    return redirect("../../")
                except Exception as e:
                    ActivityLog.log("contact.reply_failed", str(e),
                                    level="error", actor=request.user.email,
                                    contact_message_id=msg.id, subject=subject)
                    messages.error(request, f"Reply failed: {e}")
        else:
            greeting = f"Hi {msg.name.split()[0]}," if msg.name else "Hi,"
            form = ContactReplyForm(initial={
                "subject": default_subject,
                "message": f"{greeting}\n\nThanks for reaching out to Dolphin Island Tours.\n\n",
            })

        return render(request, "admin/reply_contact.html",
                      {"form": form, "message_obj": msg, "title": f"Reply to {msg.name}"})

    def send_promotional_email(self, request, queryset):
        return send_promotional_email_action(
            self,
            request,
            queryset,
            "contact messages",
            lambda obj: obj.email,
        )
    send_promotional_email.short_description = "Send promotional email to selected contacts"


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "level_badge", "action", "actor", "message")
    list_filter = ("level", "action", "created_at")
    search_fields = ("action", "actor", "message")
    readonly_fields = ("level", "action", "actor", "message", "metadata", "created_at")
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def level_badge(self, obj):
        colors = {"info": "#1389b1", "warn": "#d97706", "error": "#dc2626", "success": "#059669"}
        return format_html('<span style="background:{};color:#fff;padding:2px 8px;border-radius:10px;font-size:11px">{}</span>',
                           colors.get(obj.level, "#666"), obj.level.upper())
    level_badge.short_description = "Level"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "username", "first_name", "last_name", "phone", "accepts_marketing", "is_staff", "is_superuser")
    list_filter = BaseUserAdmin.list_filter + ("accepts_marketing",)
    search_fields = ("email", "username", "phone")
    fieldsets = BaseUserAdmin.fieldsets + (("Extra", {"fields": ("phone", "accepts_marketing")}),)
    actions = ["send_promotional_email"]

    staff_guard_message = "Only the superuser can edit or delete staff/admin accounts."

    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            return super().get_fieldsets(request, obj)
        return (
            (None, {"fields": ("email", "username", "password")}),
            ("Personal info", {"fields": ("first_name", "last_name", "phone")}),
            ("Marketing", {"fields": ("accepts_marketing",)}),
            ("Important dates", {"fields": ("last_login", "date_joined")}),
        )

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        if not request.user.is_superuser:
            readonly.extend(["last_login", "date_joined"])
        return readonly

    def has_change_permission(self, request, obj=None):
        allowed = super().has_change_permission(request, obj)
        if not allowed:
            return False
        if obj and (obj.is_staff or obj.is_superuser) and not request.user.is_superuser:
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        allowed = super().has_delete_permission(request, obj)
        if not allowed:
            return False
        if obj and (obj.is_staff or obj.is_superuser) and not request.user.is_superuser:
            return False
        return True

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.is_staff = False
            obj.is_superuser = False
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        if not request.user.is_superuser and (obj.is_staff or obj.is_superuser):
            self.message_user(request, self.staff_guard_message, level=messages.ERROR)
            return
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        if request.user.is_superuser:
            return super().delete_queryset(request, queryset)
        regular_users = queryset.filter(is_staff=False, is_superuser=False)
        blocked_count = queryset.exclude(pk__in=regular_users.values("pk")).count()
        if blocked_count:
            self.message_user(request, self.staff_guard_message, level=messages.ERROR)
        if regular_users.exists():
            super().delete_queryset(request, regular_users)

    def send_promotional_email(self, request, queryset):
        return send_promotional_email_action(
            self,
            request,
            queryset,
            "users",
            lambda obj: obj.email,
        )
    send_promotional_email.short_description = "Send promotional email to selected users"


@admin.register(TourSlot)
class TourSlotAdmin(admin.ModelAdmin):
    list_display = ("tour", "date", "time", "capacity", "seats_booked", "seats_remaining", "is_active", "notes")
    list_filter = ("is_active", "tour", "date")
    list_editable = ("capacity", "is_active")
    date_hierarchy = "date"
    ordering = ("date", "time")
    change_list_template = "admin/tourslot_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        return [path("bulk-create/", self.admin_site.admin_view(self.bulk_create), name="tourslot-bulk")] + urls

    def bulk_create(self, request):
        if request.method == "POST":
            form = BulkSlotForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                times = [datetime.strptime(t.strip(), "%H:%M").time()
                         for t in cd["times"].split(",") if t.strip()]
                weekdays = set(int(w) for w in cd["weekdays"])
                d = cd["start_date"]
                created = 0
                while d <= cd["end_date"]:
                    if d.weekday() in weekdays:
                        for tm in times:
                            _, made = TourSlot.objects.get_or_create(
                                tour=cd["tour"], date=d, time=tm,
                                defaults={"capacity": cd["capacity"], "is_active": True},
                            )
                            if made:
                                created += 1
                    d += timedelta(days=1)
                messages.success(request, f"Created {created} slots.")
                return redirect("..")
        else:
            form = BulkSlotForm()
        return render(request, "admin/bulk_slots.html", {"form": form, "title": "Bulk create slots"})


class CancelBookingForm(forms.Form):
    reason = forms.CharField(widget=forms.Textarea(attrs={"rows": 4}),
                             initial="Cancelled due to weather conditions for guest safety.",
                             help_text="Shown to the customer in their cancellation email.")
    include_alternatives = forms.BooleanField(required=False, initial=True,
                                              label="Suggest alternative departures in the email")
    refund_now = forms.BooleanField(required=False, initial=True,
                                    label="Mark refunded (process refund in payment processor separately)")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("customer_name", "customer_email", "slot", "party_size", "total_display", "status", "cancel_link", "created_at")
    list_filter = ("status", "slot__date", "slot__tour")
    search_fields = ("customer_name", "customer_email", "square_payment_id", "id")
    readonly_fields = ("id", "square_payment_id", "square_order_id", "tax_cents", "total_cents", "traveler_list", "created_at", "updated_at")
    fieldsets = (
        ("Booking", {"fields": ("id", "user", "slot", "party_size", "status")}),
        ("Customer", {"fields": ("customer_name", "customer_email", "customer_phone")}),
        ("Travelers", {"fields": ("traveler_list", "travelers")}),
        ("Payment", {"fields": ("price_per_person_cents", "discount_cents", "tax_cents", "total_cents", "promo_code", "square_payment_id", "square_order_id")}),
        ("Notes", {"fields": ("special_requests",)}),
        ("Dates", {"fields": ("created_at", "updated_at")}),
    )
    actions = ["bulk_cancel", "send_promotional_email"]

    def total_display(self, obj):
        return f"${obj.total_cents/100:.2f}"
    total_display.short_description = "Total"

    def traveler_list(self, obj):
        if not obj or not obj.travelers:
            return "No traveler details recorded."
        rows = format_html_join(
            "",
            "<li>{} — age {}</li>",
            ((t.get("name", ""), t.get("age", "")) for t in obj.travelers),
        )
        return format_html("<ol style='margin:0;padding-left:18px'>{}</ol>", rows)
    traveler_list.short_description = "Traveler list"

    def cancel_link(self, obj):
        if obj.status in ("cancelled", "refunded"):
            return format_html('<span style="color:#888">—</span>')
        return format_html('<a class="button" style="background:#dc2626;color:#fff;padding:3px 10px;border-radius:4px;text-decoration:none" href="{}">Cancel</a>',
                           f"./{obj.id}/cancel/")
    cancel_link.short_description = "Action"

    def get_urls(self):
        urls = super().get_urls()
        return [path("<uuid:booking_id>/cancel/", self.admin_site.admin_view(self.cancel_view),
                     name="booking-cancel")] + urls

    def _alternatives(self, booking):
        from django.utils import timezone as tz
        from datetime import timedelta
        future = tz.now().date()
        end = future + timedelta(days=21)
        qs = TourSlot.objects.filter(tour=booking.slot.tour, is_active=True,
                                     date__gte=future, date__lte=end).exclude(pk=booking.slot.pk).order_by("date", "time")
        out = []
        for s in qs:
            if s.seats_remaining >= booking.party_size:
                out.append({"date": s.date.isoformat(), "time": s.time.strftime("%H:%M"),
                            "seats_remaining": s.seats_remaining})
                if len(out) >= 8:
                    break
        return out

    def cancel_view(self, request, booking_id):
        booking = Booking.objects.get(pk=booking_id)
        if request.method == "POST":
            form = CancelBookingForm(request.POST)
            if form.is_valid():
                from .emails import send_email, booking_cancelled_html
                reason = form.cleaned_data["reason"]
                alternatives = self._alternatives(booking) if form.cleaned_data["include_alternatives"] else None
                booking.status = "refunded" if form.cleaned_data["refund_now"] else "cancelled"
                booking.save()
                ActivityLog.log("booking.cancelled_by_admin",
                                f"{booking.customer_name} – reason: {reason[:120]}",
                                level="warn", actor=request.user.email,
                                booking_id=str(booking.id), refund=form.cleaned_data["refund_now"])
                try:
                    send_email(booking.customer_email,
                               f"Tour cancelled – {booking.slot.tour.name} on {booking.slot.date}",
                               booking_cancelled_html(booking, reason, alternatives))
                    ActivityLog.log("booking.cancel_email_sent", booking.customer_email,
                                    level="success", actor=request.user.email)
                except Exception as e:
                    ActivityLog.log("booking.cancel_email_failed", str(e),
                                    level="error", actor=request.user.email)
                    messages.warning(request, f"Booking cancelled but email failed: {e}")
                messages.success(request, f"Cancelled {booking.id} and emailed {booking.customer_email}.")
                return redirect("../../")
        else:
            form = CancelBookingForm()
        return render(request, "admin/cancel_booking.html",
                      {"form": form, "booking": booking, "alternatives": self._alternatives(booking),
                       "title": f"Cancel booking · {booking.customer_name}"})

    def bulk_cancel(self, request, queryset):
        """Quick bulk cancel with default reason (no per-booking form)."""
        from .emails import send_email, booking_cancelled_html
        reason = "Cancelled by Dolphin Island Tours. We'll be in touch to reschedule or refund."
        sent = 0
        for b in queryset.exclude(status__in=("cancelled", "refunded")):
            b.status = "cancelled"
            b.save()
            try:
                send_email(b.customer_email,
                           f"Tour cancelled – {b.slot.tour.name} on {b.slot.date}",
                           booking_cancelled_html(b, reason, self._alternatives(b)))
                sent += 1
            except Exception:
                pass
            ActivityLog.log("booking.cancelled_by_admin", f"bulk – {b.customer_name}",
                            level="warn", actor=request.user.email, booking_id=str(b.id))
        messages.success(request, f"Cancelled {queryset.count()} bookings, sent {sent} emails.")
    bulk_cancel.short_description = "Cancel selected bookings + email customers"

    def send_promotional_email(self, request, queryset):
        return send_promotional_email_action(
            self,
            request,
            queryset,
            "bookings",
            lambda obj: obj.customer_email,
        )
    send_promotional_email.short_description = "Send promotional email to selected booking customers"


# ============== Mailing list, Promo codes, Email campaigns ==============

def _gen_promo_code(prefix="PROMO"):
    alphabet = string.ascii_uppercase + string.digits.replace("0", "").replace("1", "")
    while True:
        suffix = "".join(secrets.choice(alphabet) for _ in range(6))
        code = f"{prefix}-{suffix}"
        if not PromoCode.objects.filter(code=code).exists():
            return code


@admin.register(MailingListEntry)
class MailingListEntryAdmin(admin.ModelAdmin):
    list_display = ("email", "name", "tags", "subscribed", "created_at")
    list_filter = ("subscribed",)
    search_fields = ("email", "name", "tags")
    list_editable = ("subscribed",)


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "label", "kind", "discount_display", "used_count",
                    "max_uses", "locked_to_email", "is_active", "expires_at", "campaign")
    list_filter = ("kind", "is_active", "campaign")
    search_fields = ("code", "label", "locked_to_email")
    readonly_fields = ("used_count", "created_at")

    def discount_display(self, obj):
        if obj.kind == "percent":
            return f"{obj.percent_off}%"
        return f"${obj.amount_off_cents/100:.2f}"
    discount_display.short_description = "Discount"


@admin.register(EmailCampaign)
class EmailCampaignAdmin(admin.ModelAdmin):
    list_display = ("name", "subject", "audience", "status", "sent_count",
                    "failed_count", "last_run_at", "send_button")
    list_filter = ("status", "audience", "attach_promo")
    search_fields = ("name", "subject")
    readonly_fields = ("status", "sent_count", "failed_count", "last_run_at", "created_at")
    fieldsets = (
        ("Campaign", {"fields": ("name", "subject", "body")}),
        ("Audience", {"fields": ("audience", "manual_emails"),
                      "description": "Pick audience. Manual emails (one per line) get added on top."}),
        ("Call to action (optional)", {"fields": ("cta_label", "cta_url")}),
        ("Promo code (optional)", {"fields": ("attach_promo", "promo_kind",
                                              "promo_percent_off", "promo_amount_off_cents",
                                              "promo_expires_at"),
                                   "description": "If enabled, each recipient gets a UNIQUE single-use promo code in their email."}),
        ("Status", {"fields": ("status", "sent_count", "failed_count", "last_run_at"),
                    "classes": ("collapse",)}),
    )

    def send_button(self, obj):
        if obj.status == "sent":
            return format_html(
                '<span style="color:#059669">✓ Sent</span> '
                '<a class="button" style="background:#0b6a8a;color:#fff;padding:3px 10px;border-radius:4px;text-decoration:none;margin-left:6px" href="{}/send/">Resend</a>',
                obj.pk,
            )
        if obj.status == "failed":
            return format_html(
                '<span style="color:#dc2626">✗ Failed</span> '
                '<a class="button" style="background:#dc2626;color:#fff;padding:3px 10px;border-radius:4px;text-decoration:none;margin-left:6px" href="{}/send/">Retry</a>',
                obj.pk,
            )
        return format_html('<a class="button" style="background:#1389b1;color:#fff;padding:3px 10px;border-radius:4px;text-decoration:none" href="{}/send/">Send now</a>', obj.pk)
    send_button.short_description = "Action"

    def get_urls(self):
        urls = super().get_urls()
        return [path("<int:campaign_id>/send/", self.admin_site.admin_view(self.send_view),
                     name="campaign-send")] + urls

    def send_view(self, request, campaign_id):
        campaign = EmailCampaign.objects.get(pk=campaign_id)
        recipients = campaign.collect_recipients()
        if request.method == "POST":
            from .emails import send_email, campaign_email_html
            campaign.status = "sending"
            campaign.save(update_fields=["status"])
            sent, failed = 0, 0
            for email, name in recipients:
                promo_code = ""
                if campaign.attach_promo:
                    pc = PromoCode.objects.create(
                        code=_gen_promo_code(prefix=f"DI{campaign.pk}"),
                        label=f"Campaign #{campaign.pk} – {campaign.name}",
                        kind=campaign.promo_kind,
                        percent_off=campaign.promo_percent_off,
                        amount_off_cents=campaign.promo_amount_off_cents,
                        max_uses=1, locked_to_email=email,
                        expires_at=campaign.promo_expires_at,
                        campaign=campaign,
                    )
                    promo_code = pc.code
                try:
                    send_email(email, campaign.subject,
                               campaign_email_html(campaign.body, name=name, promo_code=promo_code,
                                                   cta_label=campaign.cta_label, cta_url=campaign.cta_url,
                                                   subject_line=""))
                    sent += 1
                except Exception as e:
                    failed += 1
                    ActivityLog.log("campaign.send_failed", f"{email}: {e}",
                                    level="error", actor=request.user.email, campaign=campaign.pk)
            campaign.status = "sent" if failed == 0 else ("failed" if sent == 0 else "sent")
            campaign.sent_count = sent
            campaign.failed_count = failed
            campaign.last_run_at = timezone.now()
            campaign.save(update_fields=["status", "sent_count", "failed_count", "last_run_at"])
            ActivityLog.log("campaign.sent", f"{campaign.name} – {sent} sent, {failed} failed",
                            level="success" if failed == 0 else "warn",
                            actor=request.user.email, campaign=campaign.pk,
                            recipients=len(recipients))
            messages.success(request, f"Campaign sent: {sent} delivered, {failed} failed.")
            return redirect(reverse("admin:api_emailcampaign_change", args=[campaign.pk]))
        return render(request, "admin/campaign_send.html",
                      {"campaign": campaign, "recipients": recipients,
                       "title": f"Send · {campaign.name}"})


from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("created_at", "stars", "author_name", "tour", "title", "is_approved", "is_featured")
    list_filter = ("is_approved", "is_featured", "rating", "tour")
    list_editable = ("is_approved", "is_featured")
    search_fields = ("author_name", "author_email", "title", "body")
    readonly_fields = ("user", "booking", "created_at")
    actions = ["approve_reviews", "feature_reviews"]

    def stars(self, obj):
        return format_html('<span style="color:#f59e0b">{}</span><span style="color:#cbd5e1">{}</span>',
                           "★" * obj.rating, "★" * (5 - obj.rating))
    stars.short_description = "Rating"

    def approve_reviews(self, request, queryset):
        n = queryset.update(is_approved=True)
        self.message_user(request, f"Approved {n} reviews.")
    approve_reviews.short_description = "Approve selected reviews"

    def feature_reviews(self, request, queryset):
        n = queryset.update(is_approved=True, is_featured=True)
        self.message_user(request, f"Featured {n} reviews.")
    feature_reviews.short_description = "Approve + feature on homepage"
