import json
import os
from datetime import timedelta
from unittest.mock import patch

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.cache import cache
from django.core.management import call_command
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode

from .admin import csv_safe_cell, promotional_email_recipients
from .emails import (
    add_unsubscribe_url,
    prepare_user_email_html,
    promotional_email_html,
    send_email,
    unsubscribe_token,
)
from .models import (
    ActivityLog,
    Booking,
    ContactMessage,
    DeletedBookingReport,
    EmailDeliveryJob,
    EmailDeliveryRecipient,
    EmailCampaign,
    MailingListEntry,
    FAQItem,
    PageContent,
    PageSection,
    NavigationLink,
    PromoCode,
    Review,
    SiteImage,
    SiteSettings,
    Tour,
    TourSlot,
)


User = get_user_model()
TEST_USER_EMAIL = "prerakbackup2023@gmail.com"


class ApiTestCase(TestCase):
    def setUp(self):
        cache.clear()
        self.client = Client()
        self.today = timezone.localdate()
        self.tour = Tour.objects.create(
            slug="wildlife",
            name="Wildlife Tour",
            short_description="See dolphins and manatees.",
            long_description="A guided wildlife trip.",
            duration_minutes=120,
            price_per_person=60,
            min_party=2,
            max_party=6,
            image_url="/images/wildlife.jpg",
            seo_title="Wildlife SEO Title",
            seo_description="Wildlife SEO description.",
            seo_keywords="wildlife,dolphins",
        )
        self.slot = TourSlot.objects.create(
            tour=self.tour,
            date=self.today + timedelta(days=7),
            time="09:00",
            capacity=6,
        )
        self.user = User.objects.create_user(
            username="guest",
            email=TEST_USER_EMAIL,
            password="StrongPass123",
            first_name="Guest",
            last_name="User",
            phone="5550000100",
            accepts_marketing=True,
        )

    def post_json(self, path, payload, token=None):
        headers = {}
        if token:
            headers["HTTP_AUTHORIZATION"] = f"Bearer {token}"
        return self.client.post(path, data=json.dumps(payload), content_type="application/json", **headers)

    def get_json(self, path, token=None):
        headers = {}
        if token:
            headers["HTTP_AUTHORIZATION"] = f"Bearer {token}"
        return self.client.get(path, **headers)

    def booking_payload(self, **overrides):
        payload = {
            "slot_id": self.slot.id,
            "party_size": 3,
            "customer_first_name": "Guest",
            "customer_last_name": "User",
            "customer_email": TEST_USER_EMAIL,
            "customer_phone": "5550000100",
            "travelers": [
                {"name": "Guest User", "age": 34},
                {"name": "Guest Two", "age": 32},
                {"name": "Guest Three", "age": 10},
            ],
            "special_requests": "",
        }
        payload.update(overrides)
        return payload

    def create_paid_booking(self, user=None, slot=None, party_size=2, email=None):
        user = user or self.user
        slot = slot or self.slot
        return Booking.objects.create(
            user=user,
            slot=slot,
            party_size=party_size,
            price_per_person_cents=slot.tour.price_per_person * 100,
            total_cents=slot.tour.price_per_person * 100 * party_size,
            status="paid",
            customer_first_name="Guest",
            customer_last_name="User",
            customer_name="Guest User",
            customer_email=email or user.email,
            travelers=[
                {"name": f"Guest {i + 1}", "age": 30 + i}
                for i in range(party_size)
            ],
        )

    def create_pending_booking(self, slot=None, party_size=2, minutes_old=20):
        slot = slot or self.slot
        booking = Booking.objects.create(
            user=self.user,
            slot=slot,
            party_size=party_size,
            price_per_person_cents=slot.tour.price_per_person * 100,
            total_cents=slot.tour.price_per_person * 100 * party_size,
            status="pending",
            customer_first_name="Guest",
            customer_last_name="User",
            customer_name="Guest User",
            customer_email=self.user.email,
            travelers=[
                {"name": f"Guest {i + 1}", "age": 30 + i}
                for i in range(party_size)
            ],
        )
        Booking.objects.filter(pk=booking.pk).update(
            updated_at=timezone.now() - timedelta(minutes=minutes_old)
        )
        booking.refresh_from_db()
        return booking


class CreateInitialSuperuserCommandTests(TestCase):
    def test_create_initial_superuser_creates_account_from_env(self):
        env = {
            "DJANGO_SUPERUSER_EMAIL": "patel.prerak2798@gmail.com",
            "DJANGO_SUPERUSER_USERNAME": "patel.prerak2798@gmail.com",
            "DJANGO_SUPERUSER_PASSWORD": "StrongPass123!",
            "DJANGO_SUPERUSER_FIRST_NAME": "Prerak",
            "DJANGO_SUPERUSER_LAST_NAME": "Patel",
            "DJANGO_SUPERUSER_PHONE": "3216100582",
        }

        with patch.dict(os.environ, env, clear=False):
            call_command("create_initial_superuser")

        user = User.objects.get(email=env["DJANGO_SUPERUSER_EMAIL"])
        self.assertEqual(user.username, env["DJANGO_SUPERUSER_USERNAME"])
        self.assertEqual(user.first_name, env["DJANGO_SUPERUSER_FIRST_NAME"])
        self.assertEqual(user.last_name, env["DJANGO_SUPERUSER_LAST_NAME"])
        self.assertEqual(user.phone, env["DJANGO_SUPERUSER_PHONE"])
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)
        self.assertTrue(user.check_password(env["DJANGO_SUPERUSER_PASSWORD"]))

    def test_create_initial_superuser_updates_existing_account(self):
        user = User.objects.create_user(
            username="old-admin",
            email="patel.prerak2798@gmail.com",
            password="OldPass123!",
            first_name="Old",
            last_name="Name",
            phone="3215550000",
        )
        user.is_staff = False
        user.is_superuser = False
        user.save(update_fields=["is_staff", "is_superuser"])

        env = {
            "DJANGO_SUPERUSER_EMAIL": "patel.prerak2798@gmail.com",
            "DJANGO_SUPERUSER_PASSWORD": "StrongPass123!",
            "DJANGO_SUPERUSER_FIRST_NAME": "Prerak",
            "DJANGO_SUPERUSER_LAST_NAME": "Patel",
            "DJANGO_SUPERUSER_PHONE": "3216100582",
        }

        with patch.dict(os.environ, env, clear=False):
            call_command("create_initial_superuser")

        user.refresh_from_db()
        self.assertEqual(user.username, env["DJANGO_SUPERUSER_EMAIL"])
        self.assertEqual(user.first_name, env["DJANGO_SUPERUSER_FIRST_NAME"])
        self.assertEqual(user.last_name, env["DJANGO_SUPERUSER_LAST_NAME"])
        self.assertEqual(user.phone, env["DJANGO_SUPERUSER_PHONE"])
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password(env["DJANGO_SUPERUSER_PASSWORD"]))


class SeedCommandTests(TestCase):
    def test_seed_preserves_existing_tour_customizations(self):
        tour = Tour.objects.create(
            slug="dolphin-wildlife-excursion",
            name="Private Custom Dolphin Trip",
            short_description="Admin edited description.",
            long_description="Admin edited long description.",
            duration_minutes=45,
            price_per_person=125,
            min_party=1,
            max_party=4,
            image_url="/images/custom.jpg",
            is_active=False,
            sort_order=99,
            seo_title="Custom SEO",
            seo_description="Custom SEO description.",
            seo_keywords="custom",
        )

        call_command("seed")

        tour.refresh_from_db()
        self.assertEqual(tour.name, "Private Custom Dolphin Trip")
        self.assertEqual(tour.short_description, "Admin edited description.")
        self.assertEqual(tour.duration_minutes, 45)
        self.assertEqual(tour.price_per_person, 125)
        self.assertEqual(tour.min_party, 1)
        self.assertEqual(tour.max_party, 4)
        self.assertEqual(tour.image_url, "/images/custom.jpg")
        self.assertFalse(tour.is_active)
        self.assertEqual(tour.sort_order, 99)
        self.assertEqual(tour.seo_title, "Custom SEO")


class OptimizeSeoCommandTests(TestCase):
    def test_optimize_seo_updates_site_pages_and_tours_without_touching_copy(self):
        from api import seo_content

        PageContent.objects.update_or_create(
            page="home",
            defaults={"hero_title": "Keep me", "seo_title": "old", "seo_description": "old", "seo_keywords": "old"},
        )
        listed = Tour.objects.create(
            slug="dolphin-wildlife-excursion", name="Dolphin Wildlife Excursion",
            short_description="keep", long_description="keep", duration_minutes=120,
            price_per_person=60, min_party=3, max_party=6,
        )
        future = Tour.objects.create(
            slug="manatee-eco-tour", name="Manatee Eco Tour",
            short_description="keep", long_description="keep", duration_minutes=90,
            price_per_person=70, min_party=2, max_party=6,
        )

        call_command("optimize_seo")

        settings = SiteSettings.get()
        self.assertEqual(settings.seo_title, seo_content.SITE["seo_title"])

        home = PageContent.objects.get(page="home")
        self.assertEqual(home.seo_title, seo_content.PAGES["home"]["seo_title"])
        self.assertEqual(home.hero_title, "Keep me")  # copy untouched

        listed.refresh_from_db()
        self.assertEqual(listed.seo_title, seo_content.TOURS["dolphin-wildlife-excursion"]["seo_title"])
        self.assertEqual(listed.short_description, "keep")  # copy untouched

        future.refresh_from_db()
        # Tours not in the curated map still get ranking-ready, geo-rich SEO.
        self.assertIn("Manatee Eco Tour", future.seo_title)
        self.assertIn("Merritt Island", future.seo_keywords)


class PublicSiteAndSeoTests(ApiTestCase):
    def test_site_api_exposes_admin_seo_content_images_and_tracking_ids(self):
        settings = SiteSettings.get()
        settings.site_name = "Dolphin Island Test"
        settings.seo_title = "Admin SEO Title"
        settings.seo_description = "Admin SEO description"
        settings.seo_keywords = "boats,dolphins"
        settings.google_analytics_id = "G-TEST123"
        settings.google_tag_manager_id = "GTM-TEST123"
        settings.meta_pixel_id = "123456789"
        settings.save()
        hero, _ = SiteImage.objects.update_or_create(
            key="hero",
            defaults={"default_path": "/images/admin-hero.jpg", "alt_text": "Hero"},
        )
        page, _ = PageContent.objects.update_or_create(
            page="home",
            defaults={
                "hero_image": hero,
                "seo_title": "Home SEO Title",
                "seo_description": "Home SEO description",
                "seo_keywords": "home,dolphin",
                "hero_title": "Admin managed hero",
            },
        )
        PageSection.objects.create(
            page_content=page,
            eyebrow="Sale",
            title="Summer offer",
            body="Save on select departures this week.",
            image=hero,
            style="sunset",
            cta_label="Book now",
            cta_url="/tours",
        )
        NavigationLink.objects.create(area="header", label="Gift cards", url="/gift", sort_order=5)
        FAQItem.objects.create(question="Can I edit FAQs?", answer="Yes, from admin.", sort_order=5)

        res = self.client.get("/api/site/")

        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertEqual(body["seo_title"], "Admin SEO Title")
        self.assertEqual(body["google_analytics_id"], "G-TEST123")
        self.assertEqual(body["google_tag_manager_id"], "GTM-TEST123")
        self.assertEqual(body["meta_pixel_id"], "123456789")
        self.assertEqual(body["images"]["hero"]["image_url"], "/images/admin-hero.jpg")
        self.assertEqual(body["pages"]["home"]["seo_title"], "Home SEO Title")
        self.assertEqual(body["pages"]["home"]["hero_image_url"], "/images/admin-hero.jpg")
        self.assertEqual(body["pages"]["home"]["sections"][0]["title"], "Summer offer")
        self.assertEqual(body["pages"]["home"]["sections"][0]["image_url"], "/images/admin-hero.jpg")
        self.assertEqual(body["pages"]["home"]["sections"][0]["style"], "sunset")
        self.assertEqual(body["navigation"]["header"][0]["label"], "Gift cards")
        self.assertEqual(body["faqs"][0]["question"], "Can I edit FAQs?")

    def test_tour_api_exposes_admin_seo_fields(self):
        res = self.client.get("/api/tours/")

        self.assertEqual(res.status_code, 200)
        tour = res.json()[0]
        self.assertEqual(tour["seo_title"], "Wildlife SEO Title")
        self.assertEqual(tour["seo_description"], "Wildlife SEO description.")
        self.assertEqual(tour["seo_keywords"], "wildlife,dolphins")

    @override_settings(FRONTEND_URL="https://example.test")
    def test_sitemap_robots_and_inactive_tours(self):
        Tour.objects.create(
            slug="inactive",
            name="Inactive",
            short_description="Hidden",
            price_per_person=60,
            is_active=False,
        )
        SiteSettings.get().save()

        sitemap = self.client.get("/api/sitemap.xml")
        root_sitemap = self.client.get("/sitemap.xml")
        robots = self.client.get("/api/robots.txt")
        root_robots = self.client.get("/robots.txt")
        sitemap_head = self.client.head("/api/sitemap.xml")
        root_sitemap_head = self.client.head("/sitemap.xml")
        robots_head = self.client.head("/api/robots.txt")
        root_robots_head = self.client.head("/robots.txt")

        self.assertEqual(sitemap.status_code, 200)
        self.assertEqual(root_sitemap.status_code, 200)
        self.assertEqual(sitemap_head.status_code, 200)
        self.assertEqual(root_sitemap_head.status_code, 200)
        self.assertContains(sitemap, "https://example.test/tours/wildlife")
        self.assertContains(root_sitemap, "<changefreq>weekly</changefreq>")
        self.assertNotContains(sitemap, "inactive")
        self.assertEqual(robots.status_code, 200)
        self.assertEqual(root_robots.status_code, 200)
        self.assertEqual(robots_head.status_code, 200)
        self.assertEqual(root_robots_head.status_code, 200)
        self.assertIn("text/plain", robots["Content-Type"])
        self.assertContains(robots, "User-agent")
        self.assertContains(root_robots, "Sitemap:")

    def test_admin_pages_render_seo_fields_for_editing(self):
        admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="StrongPass123",
        )
        settings = SiteSettings.get()
        page, _ = PageContent.objects.update_or_create(
            page="about",
            defaults={"seo_title": "About SEO"},
        )
        self.client.force_login(admin_user)

        site_res = self.client.get(reverse("admin:api_sitesettings_change", args=[settings.pk]))
        page_res = self.client.get(reverse("admin:api_pagecontent_change", args=[page.pk]))
        tour_res = self.client.get(reverse("admin:api_tour_change", args=[self.tour.pk]))

        self.assertContains(site_res, 'name="seo_title"')
        self.assertContains(site_res, 'name="seo_description"')
        self.assertContains(page_res, 'name="seo_keywords"')
        self.assertContains(tour_res, 'name="og_image"')

    def test_admin_can_create_user_with_required_profile_fields(self):
        admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="StrongPass123",
            first_name="Admin",
            last_name="User",
            phone="5550000000",
        )
        self.client.force_login(admin_user)

        res = self.client.post(reverse("admin:api_user_add"), {
            "email": "admin-created@example.com",
            "username": "admincreated",
            "first_name": "Admin",
            "last_name": "Created",
            "phone": "5550000002",
            "accepts_marketing": "on",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        }, follow=True)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(User.objects.filter(email="admin-created@example.com").exists())

    def test_admin_booking_list_displays_square_payment_references(self):
        admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="StrongPass123",
            first_name="Admin",
            last_name="User",
            phone="5550000000",
        )
        self.create_paid_booking()
        Booking.objects.update(
            square_payment_id="sq-payment-test",
            square_order_id="sq-order-test",
        )
        self.client.force_login(admin_user)

        res = self.client.get(reverse("admin:api_booking_changelist"))

        self.assertContains(res, "sq-payment-test")
        self.assertContains(res, "sq-order-test")

    def test_admin_reports_and_downloads_render(self):
        admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="StrongPass123",
            first_name="Admin",
            last_name="User",
            phone="5550000000",
        )
        self.create_paid_booking()
        self.client.force_login(admin_user)

        bookings_csv = self.client.get(reverse("admin:api_reports_bookings_csv"))
        users_csv = self.client.get(reverse("admin:api_reports_users_csv"))
        taxes_csv = self.client.get(reverse("admin:api_reports_taxes_csv"))
        reports = self.client.get(reverse("admin:api_reports"))
        payments_csv = self.client.get(reverse("admin:api_reports_payments_csv"))

        self.assertEqual(reports.status_code, 200)
        self.assertContains(reports, "Recent payment rows")
        self.assertNotContains(reports, "Analytics")

        self.assertNotContains(reports, "Deleted archived")
        self.assertContains(bookings_csv, "transaction_id,transaction_date,transaction_time")
        self.assertContains(payments_csv, "transaction_id,transaction_date,transaction_time,record_state,status")
        self.assertContains(bookings_csv, TEST_USER_EMAIL)
        self.assertContains(users_csv, "paid_bookings,income_usd")
        self.assertNotContains(users_csv, "page_views")
        self.assertContains(taxes_csv, "gross_sales_usd,discount_usd,taxable_sales_usd,tax_collected_usd")

    def test_csv_exports_escape_formula_injection_cells(self):
        self.create_paid_booking(email="=cmd@example.com")
        Booking.objects.update(special_requests=" =HYPERLINK(\"https://evil.test\")")
        admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="StrongPass123",
            first_name="Admin",
            last_name="User",
            phone="5550000000",
        )
        self.client.force_login(admin_user)

        res = self.client.get(reverse("admin:api_reports_bookings_csv"))

        self.assertContains(res, "'=cmd@example.com")
        self.assertContains(res, "' =HYPERLINK")
        self.assertEqual(csv_safe_cell("@bad"), "'@bad")
        self.assertEqual(csv_safe_cell("  +bad"), "'  +bad")

    def test_admin_reports_include_cancelled_refunded_and_deleted_bookings(self):
        admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="StrongPass123",
            first_name="Admin",
            last_name="User",
            phone="5550000000",
        )
        cancelled = self.create_paid_booking(email="cancelled@example.com")
        refunded = self.create_paid_booking(email="refunded@example.com")
        cancelled.status = "cancelled"
        cancelled.save(update_fields=["status"])
        refunded.status = "refunded"
        refunded.save(update_fields=["status"])
        self.client.force_login(admin_user)

        bookings_csv = self.client.get(reverse("admin:api_reports_bookings_csv"))
        taxes_csv = self.client.get(reverse("admin:api_reports_taxes_csv"))
        self.assertContains(bookings_csv, "cancelled@example.com")
        self.assertContains(bookings_csv, "refunded@example.com")
        self.assertContains(bookings_csv, "cancelled")
        self.assertContains(bookings_csv, "refunded")
        self.assertContains(taxes_csv, "cancelled@example.com")
        self.assertContains(taxes_csv, "refunded@example.com")

        delete_confirm = self.client.post(
            reverse("admin:api_booking_delete", args=[cancelled.pk]),
            {"post": "yes"},
            follow=True,
        )
        self.assertEqual(delete_confirm.status_code, 200)
        self.assertFalse(Booking.objects.filter(pk=cancelled.pk).exists())
        archived = DeletedBookingReport.objects.get(booking_id=cancelled.pk)
        self.assertEqual(archived.deleted_by, "admin@example.com")

        bookings_after_delete = self.client.get(reverse("admin:api_reports_bookings_csv"))
        taxes_after_delete = self.client.get(reverse("admin:api_reports_taxes_csv"))
        reports_after_delete = self.client.get(reverse("admin:api_reports"))
        payments_after_delete = self.client.get(reverse("admin:api_reports_payments_csv"))
        admin_index = self.client.get(reverse("admin:index"))

        self.assertContains(bookings_after_delete, "cancelled@example.com")
        self.assertContains(bookings_after_delete, "deleted")
        self.assertContains(taxes_after_delete, "cancelled@example.com")
        self.assertContains(taxes_after_delete, "deleted")
        self.assertContains(reports_after_delete, "cancelled@example.com")
        self.assertContains(reports_after_delete, "deleted")
        self.assertContains(payments_after_delete, "cancelled@example.com")
        self.assertContains(payments_after_delete, "deleted")
        self.assertContains(payments_after_delete, "admin@example.com")
        self.assertNotContains(admin_index, "Deleted booking report")


class AuthContactAndSlotSafetyTests(ApiTestCase):
    def test_customer_auth_endpoints_are_removed(self):
        """Customer login/signup/account were removed; only Django admin remains."""
        self.assertEqual(self.post_json("/api/auth/login/", {"email": TEST_USER_EMAIL, "password": "StrongPass123"}).status_code, 404)
        self.assertEqual(self.post_json("/api/auth/signup/", {"email": "x@example.com"}).status_code, 404)
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 404)
        self.assertEqual(self.post_json("/api/auth/password-reset/", {"email": TEST_USER_EMAIL}).status_code, 404)
        # No customer booking list endpoint either.
        self.assertEqual(self.client.get("/api/bookings/").status_code, 404)

    def test_contact_form_creates_message(self):
        res = self.post_json("/api/contact/", {
            "name": "Visitor",
            "email": "visitor@example.com",
            "phone": "",
            "subject": "Question",
            "message": "Can we bring kids?",
        })

        self.assertEqual(res.status_code, 201)
        self.assertTrue(ContactMessage.objects.filter(email="visitor@example.com").exists())

    def test_contact_rate_limit_blocks_abuse(self):
        contact_responses = [
            self.post_json("/api/contact/", {
                "name": "Visitor",
                "email": f"visitor-{i}@example.com",
                "message": "Can we bring kids?",
            })
            for i in range(6)
        ]

        self.assertEqual([r.status_code for r in contact_responses[:5]], [201] * 5)
        self.assertEqual(contact_responses[5].status_code, 429)

    def test_slots_and_dates_hide_past_inactive_and_full_departures(self):
        past = TourSlot.objects.create(
            tour=self.tour,
            date=self.today - timedelta(days=1),
            time="10:00",
            capacity=6,
        )
        inactive = TourSlot.objects.create(
            tour=self.tour,
            date=self.today + timedelta(days=8),
            time="11:00",
            capacity=6,
            is_active=False,
        )
        full = TourSlot.objects.create(
            tour=self.tour,
            date=self.today + timedelta(days=9),
            time="12:00",
            capacity=2,
        )
        self.create_paid_booking(slot=full, party_size=2)

        slots = self.client.get("/api/slots/?tour=wildlife").json()
        dates = self.client.get("/api/tours/wildlife/dates/").json()["dates"]
        ids = {row["id"] for row in slots}

        self.assertIn(self.slot.id, ids)
        self.assertNotIn(past.id, ids)
        self.assertNotIn(inactive.id, ids)
        self.assertEqual(full.seats_remaining, 0)
        self.assertNotIn(full.date.isoformat(), dates)

    def test_slot_detail_returns_one_bookable_departure(self):
        res = self.client.get(f"/api/slots/{self.slot.id}/")

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["id"], self.slot.id)
        self.assertEqual(res.json()["tour"]["slug"], self.tour.slug)
        self.assertEqual(res.json()["seats_remaining"], self.slot.capacity)

    @override_settings(PENDING_BOOKING_EXPIRY_MINUTES=15)
    def test_stale_pending_booking_holds_expire_and_release_seats(self):
        pending = self.create_pending_booking(party_size=5, minutes_old=20)

        slots = self.client.get("/api/slots/?tour=wildlife").json()
        pending.refresh_from_db()

        self.assertEqual(pending.status, "expired")
        self.assertEqual(slots[0]["seats_remaining"], 6)

    @override_settings(PENDING_BOOKING_EXPIRY_MINUTES=15)
    def test_expire_pending_bookings_management_command(self):
        stale = self.create_pending_booking(party_size=2, minutes_old=20)
        fresh = self.create_pending_booking(party_size=2, minutes_old=5)

        call_command("expire_pending_bookings", verbosity=0)
        stale.refresh_from_db()
        fresh.refresh_from_db()

        self.assertEqual(stale.status, "expired")
        self.assertEqual(fresh.status, "pending")


@override_settings(FAKE_PAYMENTS=True, RESEND_API_KEY="", SMTP_HOST="", ADMIN_EMAIL="admin@example.com")
class BookingAndPromoTests(ApiTestCase):
    def test_guest_lookup_returns_matching_booking_by_email_and_last_name(self):
        booking = self.create_paid_booking(user=None, email="guest.lookup@example.com")
        booking.customer_first_name = "Alex"
        booking.customer_last_name = "Buyer"
        booking.customer_name = "Alex Buyer"
        booking.save(update_fields=["customer_first_name", "customer_last_name", "customer_name"])

        res = self.post_json("/api/bookings/lookup/", {
            "email": "GUEST.LOOKUP@example.com",
            "last_name": "Buyer",
        })

        self.assertEqual(res.status_code, 200, res.content)
        body = res.json()
        self.assertEqual(len(body["results"]), 1)
        self.assertEqual(body["results"][0]["id"], str(booking.id))
        self.assertEqual(body["results"][0]["customer_email"], "guest.lookup@example.com")
        self.assertEqual(body["results"][0]["customer_last_name"], "Buyer")

    def test_guest_lookup_does_not_return_wrong_last_name(self):
        booking = self.create_paid_booking(user=None, email="guest.lookup@example.com")
        booking.customer_first_name = "Alex"
        booking.customer_last_name = "Buyer"
        booking.customer_name = "Alex Buyer"
        booking.save(update_fields=["customer_first_name", "customer_last_name", "customer_name"])

        res = self.post_json("/api/bookings/lookup/", {
            "email": "guest.lookup@example.com",
            "last_name": "Other",
        })

        self.assertEqual(res.status_code, 200, res.content)
        self.assertEqual(res.json()["results"], [])

    def test_guest_create_and_pay_fake_payment_creates_paid_booking(self):
        res = self.post_json("/api/bookings/create-and-pay/", self.booking_payload())

        self.assertEqual(res.status_code, 201, res.content)
        body = res.json()
        self.assertEqual(body["status"], "paid")
        self.assertEqual(body["total_cents"], 18000)
        self.assertEqual(body["slot"]["seats_remaining"], 3)
        self.assertEqual(len(body["travelers"]), 3)
        self.assertEqual(body["travelers"][0]["name"], "Guest User")
        self.assertEqual(body["customer_first_name"], "Guest")
        self.assertEqual(body["customer_last_name"], "User")
        self.assertEqual(body["customer_name"], "Guest User")
        self.assertTrue(Booking.objects.filter(user__isnull=True, customer_email=TEST_USER_EMAIL, status="paid").exists())
        audit = ActivityLog.objects.get(action="booking_payment_verified")
        self.assertEqual(audit.actor, TEST_USER_EMAIL)
        self.assertEqual(audit.metadata["total_cents"], 18000)
        self.assertEqual(EmailDeliveryJob.objects.filter(source__startswith="txn:").count(), 2)
        self.assertTrue(
            EmailDeliveryRecipient.objects.filter(
                email=self.user.email,
                subject="Your Dolphin Island Tours booking",
                status="pending",
            ).exists()
        )
        self.assertTrue(
            EmailDeliveryRecipient.objects.filter(
                email="admin@example.com",
                subject="New booking: Guest User",
                status="pending",
            ).exists()
        )

    def test_create_and_pay_requires_first_and_last_name(self):
        missing_last = self.post_json(
            "/api/bookings/create-and-pay/",
            self.booking_payload(customer_last_name="   "),
        )
        self.assertEqual(missing_last.status_code, 400)
        self.assertIn("customer_last_name", missing_last.json())
        self.assertEqual(Booking.objects.count(), 0)

    def test_guest_lookup_falls_back_to_full_name_for_legacy_bookings(self):
        booking = self.create_paid_booking(user=None, email="legacy@example.com")
        # Legacy row: only the combined name was stored.
        Booking.objects.filter(pk=booking.pk).update(
            customer_first_name="", customer_last_name="", customer_name="Jordan Rivera",
        )

        res = self.post_json("/api/bookings/lookup/", {
            "email": "legacy@example.com",
            "last_name": "Rivera",
        })

        self.assertEqual(res.status_code, 200, res.content)
        self.assertEqual(len(res.json()["results"]), 1)

    @override_settings(FAKE_PAYMENTS=False)
    def test_real_payment_mode_requires_source_id_before_creating_booking(self):
        res = self.post_json("/api/bookings/create-and-pay/", self.booking_payload())

        self.assertEqual(res.status_code, 400)
        self.assertEqual(Booking.objects.count(), 0)

    @override_settings(FAKE_PAYMENTS=False)
    def test_declined_payment_marks_attempt_failed_without_sending_receipt(self):
        with patch("api.views.charge", side_effect=RuntimeError("Square error: CARD_DECLINED")):
            res = self.post_json(
                "/api/bookings/create-and-pay/",
                self.booking_payload(source_id="cnon:card-nonce"),
            )

        self.assertEqual(res.status_code, 402)
        self.assertIn("No charge was made", res.json()["detail"])
        booking = Booking.objects.get()
        self.assertEqual(booking.status, "payment_failed")
        self.assertFalse(booking.square_payment_id)
        self.assertEqual(EmailDeliveryJob.objects.count(), 0)
        self.assertEqual(EmailDeliveryRecipient.objects.count(), 0)
        audit = ActivityLog.objects.get(action="booking_payment_failed")
        self.assertEqual(audit.metadata["booking_id"], str(booking.id))

    @override_settings(FAKE_PAYMENTS=False)
    def test_real_payment_sends_itemized_amounts_to_square(self):
        self.tour.price_per_person = 5
        self.tour.tax_rate_percent = "1.00"
        self.tour.save(update_fields=["price_per_person", "tax_rate_percent"])

        with patch("api.views.charge", return_value={"id": "sq-payment", "order_id": "sq-order"}) as charge_mock:
            res = self.post_json(
                "/api/bookings/create-and-pay/",
                self.booking_payload(source_id="cnon:card-nonce"),
            )

        self.assertEqual(res.status_code, 201, res.content)
        charge_mock.assert_called_once()
        args, kwargs = charge_mock.call_args
        self.assertEqual(args[:3], ("cnon:card-nonce", 1515, TEST_USER_EMAIL))
        self.assertEqual(kwargs["subtotal_cents"], 1500)
        self.assertEqual(kwargs["discount_cents"], 0)
        self.assertEqual(kwargs["tax_cents"], 15)
        self.assertEqual(str(kwargs["tax_rate_percent"]), "1.00")
        self.assertEqual(kwargs["item_name"], "Wildlife Tour")

    def test_booking_validation_rejects_party_limits_capacity_and_past_slots(self):
        past = TourSlot.objects.create(
            tour=self.tour,
            date=self.today - timedelta(days=1),
            time="10:00",
            capacity=6,
        )

        too_small = self.post_json("/api/bookings/create-and-pay/", self.booking_payload(party_size=1))
        too_large = self.post_json("/api/bookings/create-and-pay/", self.booking_payload(party_size=7))
        past_res = self.post_json("/api/bookings/create-and-pay/", self.booking_payload(slot_id=past.id))
        self.create_paid_booking(slot=self.slot, party_size=5)
        over_capacity = self.post_json("/api/bookings/create-and-pay/", self.booking_payload(party_size=2))

        self.assertEqual(too_small.status_code, 400)
        self.assertEqual(too_large.status_code, 400)
        self.assertEqual(past_res.status_code, 400)
        self.assertEqual(over_capacity.status_code, 400)

    def test_bookings_endpoint_only_exposes_create_and_pay(self):
        booking = self.create_paid_booking()

        # No customer list, retrieve, or delete routes remain on the booking API.
        self.assertEqual(self.client.get("/api/bookings/").status_code, 404)
        self.assertEqual(self.client.get(f"/api/bookings/{booking.id}/").status_code, 404)
        self.assertEqual(self.client.delete(f"/api/bookings/{booking.id}/").status_code, 404)
        self.assertTrue(Booking.objects.filter(pk=booking.pk, status="paid").exists())

    def test_promo_validation_handles_percent_amount_locked_inactive_and_expired_codes(self):
        PromoCode.objects.create(code="TEN", kind="percent", percent_off=10, max_uses=0)
        PromoCode.objects.create(code="AMOUNT", kind="amount", amount_off_cents=25000, max_uses=0)
        PromoCode.objects.create(code="LOCKED", kind="percent", percent_off=10, locked_to_email="owner@example.com")
        PromoCode.objects.create(code="OFF", kind="percent", percent_off=10, is_active=False)
        PromoCode.objects.create(
            code="OLD",
            kind="percent",
            percent_off=10,
            expires_at=timezone.now() - timedelta(hours=1),
        )

        ten = self.post_json("/api/promo/validate/", {"code": "ten", "email": "x@example.com", "subtotal_cents": 12000})
        amount = self.post_json("/api/promo/validate/", {"code": "AMOUNT", "email": "x@example.com", "subtotal_cents": 12000})
        locked_missing = self.post_json("/api/promo/validate/", {"code": "LOCKED", "subtotal_cents": 12000})
        locked_wrong = self.post_json("/api/promo/validate/", {"code": "LOCKED", "email": "wrong@example.com", "subtotal_cents": 12000})
        inactive = self.post_json("/api/promo/validate/", {"code": "OFF", "email": "x@example.com", "subtotal_cents": 12000})
        expired = self.post_json("/api/promo/validate/", {"code": "OLD", "email": "x@example.com", "subtotal_cents": 12000})

        self.assertTrue(ten.json()["valid"])
        self.assertEqual(ten.json()["discount_cents"], 1200)
        self.assertTrue(amount.json()["valid"])
        self.assertEqual(amount.json()["discount_cents"], 12000)
        self.assertFalse(locked_missing.json()["valid"])
        self.assertFalse(locked_wrong.json()["valid"])
        self.assertFalse(inactive.json()["valid"])
        self.assertFalse(expired.json()["valid"])

    def test_promo_validation_rejects_blank_code_and_zero_subtotal(self):
        blank = self.post_json("/api/promo/validate/", {
            "code": " ",
            "email": TEST_USER_EMAIL,
            "subtotal_cents": 12000,
        })
        zero_subtotal = self.post_json("/api/promo/validate/", {
            "code": "TEN",
            "email": TEST_USER_EMAIL,
            "subtotal_cents": 0,
        })

        self.assertEqual(blank.status_code, 400)
        self.assertEqual(zero_subtotal.status_code, 400)

    def test_promo_validation_rate_limit_blocks_repeated_attempts(self):
        PromoCode.objects.create(code="RATE", kind="percent", percent_off=10, max_uses=0)

        responses = [
            self.post_json(
                "/api/promo/validate/",
                {"code": "RATE", "email": TEST_USER_EMAIL, "subtotal_cents": 12000},
            )
            for _ in range(21)
        ]

        self.assertEqual([r.status_code for r in responses[:20]], [200] * 20)
        self.assertEqual(responses[20].status_code, 429)
        self.assertIn("Too many promo code attempts", responses[20].json()["detail"])

    def test_single_use_promo_is_redeemed_once_and_blocks_second_booking(self):
        PromoCode.objects.create(code="ONCE", kind="percent", percent_off=25, max_uses=1)

        first = self.post_json(
            "/api/bookings/create-and-pay/",
            self.booking_payload(promo_code="once"),
        )
        second = self.post_json(
            "/api/bookings/create-and-pay/",
            self.booking_payload(party_size=2, promo_code="ONCE"),
        )
        validate_again = self.post_json(
            "/api/promo/validate/",
            {"code": "ONCE", "email": TEST_USER_EMAIL, "subtotal_cents": 12000},
        )

        self.assertEqual(first.status_code, 201, first.content)
        self.assertEqual(first.json()["discount_cents"], 4500)
        self.assertEqual(first.json()["total_cents"], 13500)
        self.assertEqual(PromoCode.objects.get(code="ONCE").used_count, 1)
        self.assertEqual(second.status_code, 400)
        self.assertEqual(Booking.objects.count(), 1)
        self.assertFalse(validate_again.json()["valid"])

    @override_settings(FAKE_PAYMENTS=False)
    def test_declined_payment_releases_single_use_promo_hold(self):
        PromoCode.objects.create(code="ONCE", kind="percent", percent_off=25, max_uses=1)

        with patch("api.views.charge", side_effect=RuntimeError("Square error: CARD_DECLINED")):
            declined = self.post_json(
                "/api/bookings/create-and-pay/",
                self.booking_payload(source_id="cnon:card-nonce", promo_code="ONCE"),
            )

        self.assertEqual(declined.status_code, 402)
        # Hold released: the code is redeemable again.
        self.assertEqual(PromoCode.objects.get(code="ONCE").used_count, 0)
        retry = self.post_json(
            "/api/promo/validate/",
            {"code": "ONCE", "email": TEST_USER_EMAIL, "subtotal_cents": 12000},
        )
        self.assertTrue(retry.json()["valid"])

    @override_settings(PENDING_BOOKING_EXPIRY_MINUTES=15)
    def test_expired_pending_hold_releases_promo(self):
        promo = PromoCode.objects.create(code="HOLD", kind="percent", percent_off=10, max_uses=1)
        pending = self.create_pending_booking(party_size=2, minutes_old=20)
        Booking.objects.filter(pk=pending.pk).update(promo_code=promo)
        PromoCode.objects.filter(pk=promo.pk).update(used_count=1)

        call_command("expire_pending_bookings", verbosity=0)

        pending.refresh_from_db()
        promo.refresh_from_db()
        self.assertEqual(pending.status, "expired")
        self.assertEqual(promo.used_count, 0)

    def test_promo_code_is_stored_uppercased(self):
        promo = PromoCode.objects.create(code="  summer-deal ", kind="percent", percent_off=10)
        self.assertEqual(promo.code, "SUMMER-DEAL")

    def test_locked_promo_authorization_uses_booking_email(self):
        PromoCode.objects.create(
            code="OWNER",
            kind="amount",
            amount_off_cents=5000,
            locked_to_email="owner@example.com",
            max_uses=0,
        )

        matching_email = self.post_json(
            "/api/bookings/create-and-pay/",
            self.booking_payload(customer_email="OWNER@example.com", promo_code="OWNER"),
        )
        wrong_email = self.post_json(
            "/api/bookings/create-and-pay/",
            self.booking_payload(party_size=2, customer_email="someone-else@example.com", promo_code="OWNER"),
        )

        self.assertEqual(matching_email.status_code, 201, matching_email.content)
        self.assertEqual(matching_email.json()["discount_cents"], 5000)
        self.assertEqual(wrong_email.status_code, 400)

    def test_booking_total_includes_tour_tax_rate(self):
        self.tour.tax_rate_percent = "7.50"
        self.tour.save(update_fields=["tax_rate_percent"])

        res = self.post_json("/api/bookings/create-and-pay/", self.booking_payload())

        self.assertEqual(res.status_code, 201, res.content)
        body = res.json()
        self.assertEqual(body["tax_cents"], 1350)
        self.assertEqual(body["total_cents"], 19350)

    def test_tour_zero_tax_rate_is_honored(self):
        self.tour.tax_rate_percent = "0.00"
        self.tour.save(update_fields=["tax_rate_percent"])

        res = self.post_json("/api/bookings/create-and-pay/", self.booking_payload())

        self.assertEqual(res.status_code, 201, res.content)
        body = res.json()
        self.assertEqual(body["tax_cents"], 0)
        self.assertEqual(body["total_cents"], 18000)


class FakeSquareResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload
        self.content = b"{}"
        self.text = json.dumps(payload)

    def json(self):
        return self._payload


@override_settings(
    SQUARE_ACCESS_TOKEN="test-token",
    SQUARE_LOCATION_ID="test-location",
    SQUARE_ENV="sandbox",
)
class SquarePaymentTests(TestCase):
    def test_charge_creates_taxed_square_order_then_payment(self):
        from .payments import charge

        def fake_post(url, **kwargs):
            if url.endswith("/orders"):
                return FakeSquareResponse(200, {"order": {"id": "square-order-id"}})
            if url.endswith("/payments"):
                return FakeSquareResponse(200, {"payment": {"id": "square-payment-id", "order_id": "square-order-id"}})
            raise AssertionError(f"Unexpected Square URL: {url}")

        with patch("api.payments.requests.post", side_effect=fake_post) as post_mock:
            payment = charge(
                "cnon:card-nonce",
                1515,
                TEST_USER_EMAIL,
                note="Dolphin tour 2026-06-04 09:00",
                subtotal_cents=1500,
                discount_cents=0,
                tax_cents=15,
                tax_rate_percent="1.00",
                item_name="Dolphin Wildlife Excursion",
            )

        self.assertEqual(payment, {"id": "square-payment-id", "order_id": "square-order-id"})
        self.assertEqual(post_mock.call_count, 2)
        order_call = post_mock.call_args_list[0]
        payment_call = post_mock.call_args_list[1]
        self.assertEqual(order_call.args[0], "https://connect.squareupsandbox.com/v2/orders")
        order_body = order_call.kwargs["json"]["order"]
        self.assertEqual(order_body["line_items"][0]["base_price_money"]["amount"], 1500)
        self.assertEqual(order_body["taxes"][0]["percentage"], "1.00")
        self.assertEqual(order_body["taxes"][0]["scope"], "ORDER")
        self.assertEqual(payment_call.args[0], "https://connect.squareupsandbox.com/v2/payments")
        self.assertEqual(payment_call.kwargs["json"]["amount_money"]["amount"], 1515)
        self.assertEqual(payment_call.kwargs["json"]["order_id"], "square-order-id")


class ReviewSystemRemovedTests(ApiTestCase):
    def test_legacy_local_review_api_is_not_available(self):
        responses = [
            self.client.get("/api/reviews/"),
            self.client.post("/api/reviews/", data={}, content_type="application/json"),
            self.client.get("/api/reviews/stats/"),
            self.client.get("/api/tours/wildlife/reviews/stats/"),
        ]

        self.assertTrue(all(response.status_code == 404 for response in responses))

    def test_review_model_is_not_registered_in_admin(self):
        self.assertNotIn(Review, admin.site._registry)


class AdminMarketingPromoTests(ApiTestCase):
    def test_campaign_recipient_collection_dedupes_and_requires_marketing_opt_in(self):
        User.objects.create_user(
            username="nosub",
            email="nosub@example.com",
            password="StrongPass123",
            accepts_marketing=False,
        )
        MailingListEntry.objects.update_or_create(
            email=TEST_USER_EMAIL,
            defaults={"name": "Duplicate", "subscribed": True},
        )
        MailingListEntry.objects.create(email="list@example.com", name="List", subscribed=True)
        MailingListEntry.objects.create(email="unsub@example.com", name="Unsub", subscribed=False)
        campaign = EmailCampaign.objects.create(
            name="May promo",
            subject="Deal",
            body="Hi {name}, use {promo_code}.",
            audience="both",
            manual_emails=f"manual@example.com\n{TEST_USER_EMAIL}",
        )

        recipients = campaign.collect_recipients()
        emails = {email.lower() for email, _ in recipients}

        self.assertEqual(emails, {TEST_USER_EMAIL, "list@example.com", "manual@example.com"})

    def test_campaign_admin_send_queues_unique_locked_single_use_promo_codes(self):
        admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="StrongPass123",
        )
        MailingListEntry.objects.create(email="one@example.com", name="One", subscribed=True)
        MailingListEntry.objects.create(email="two@example.com", name="Two", subscribed=True)
        campaign = EmailCampaign.objects.create(
            name="Promo",
            subject="Promo",
            body="Your code is {promo_code}",
            audience="subscribed_users",
            attach_promo=True,
            promo_kind="percent",
            promo_percent_off=15,
            promo_expires_at=timezone.now() + timedelta(days=3),
        )
        self.client.force_login(admin_user)

        res = self.client.post(reverse("admin:campaign-send", args=[campaign.pk]))

        self.assertEqual(res.status_code, 302)
        campaign.refresh_from_db()
        self.assertEqual(campaign.status, "sending")
        self.assertEqual(campaign.sent_count, 0)
        job = EmailDeliveryJob.objects.get(campaign=campaign)
        self.assertEqual(job.status, "queued")
        self.assertEqual(job.total_count, 3)
        self.assertTrue(ActivityLog.objects.filter(action="campaign_email_queued", actor="admin@example.com").exists())
        self.assertEqual(job.recipients.count(), 3)
        codes = PromoCode.objects.filter(campaign=campaign)
        self.assertEqual(codes.count(), 3)
        self.assertEqual({c.max_uses for c in codes}, {1})
        self.assertEqual({c.used_count for c in codes}, {0})
        self.assertEqual({c.locked_to_email for c in codes}, {TEST_USER_EMAIL, "one@example.com", "two@example.com"})

        with patch("api.email_queue.send_email", return_value=None) as send:
            call_command("process_email_queue", once=True, batch_size=10)

        campaign.refresh_from_db()
        job.refresh_from_db()
        self.assertEqual(send.call_count, 3)
        self.assertEqual(campaign.status, "sent")
        self.assertEqual(campaign.sent_count, 3)
        self.assertEqual(job.status, "sent")
        self.assertEqual(EmailDeliveryRecipient.objects.filter(status="sent").count(), 3)

    def test_admin_can_add_contact_message_from_button(self):
        admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="StrongPass123",
        )
        self.client.force_login(admin_user)

        add = self.client.post(reverse("admin:api_contactmessage_add"), {
            "name": "Manual Contact",
            "email": "manual-contact@example.com",
            "phone": "5550001234",
            "subject": "Manual note",
            "message": "Added by admin.",
            "handled": "",
            "_save": "Save",
        }, follow=True)

        self.assertEqual(add.status_code, 200)
        self.assertTrue(ContactMessage.objects.filter(email="manual-contact@example.com").exists())

    def test_admin_can_add_selected_app_users_to_mailing_list(self):
        admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="StrongPass123",
        )
        app_user = User.objects.create_user(
            username="appuser",
            email="app-user@example.com",
            password="StrongPass123",
            first_name="App",
            last_name="User",
            phone="5550001234",
            accepts_marketing=True,
        )
        self.client.force_login(admin_user)

        res = self.client.post(reverse("admin:api_user_changelist"), {
            "action": "add_to_mailing_list",
            "_selected_action": [app_user.pk],
        }, follow=True)

        self.assertEqual(res.status_code, 200)
        entry = MailingListEntry.objects.get(email="app-user@example.com")
        self.assertEqual(entry.name, "App User")
        self.assertEqual(entry.tags, "app-user")
        self.assertTrue(entry.subscribed)

    def test_promotional_email_action_recipient_helper_dedupes_selected_and_extra_emails(self):
        contacts = [
            ContactMessage(name="A", email="A@Example.com", message="Hi"),
            ContactMessage(name="B", email="b@example.com", message="Hi"),
            ContactMessage(name="Dup", email="a@example.com", message="Hi"),
        ]

        recipients = promotional_email_recipients(
            contacts,
            lambda obj: obj.email,
            ["B@example.com", "extra@example.com"],
        )

        self.assertEqual(recipients, ["a@example.com", "b@example.com", "extra@example.com"])

    def test_bulk_promotional_admin_action_queues_email_job_without_sending_inline(self):
        admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="StrongPass123",
        )
        contact = ContactMessage.objects.create(
            name="Visitor",
            email="visitor@example.com",
            subject="Question",
            message="Hi",
        )
        self.client.force_login(admin_user)

        with patch("api.email_queue.send_email") as send:
            res = self.client.post(reverse("admin:api_contactmessage_changelist"), {
                "action": "send_promotional_email",
                "_selected_action": [contact.pk],
                "apply": "1",
                "subject": "Bulk QA",
                "message": "Hello from QA.",
                "cta_label": "",
                "cta_url": "",
                "extra_emails": "extra@example.com",
            }, follow=True)

        self.assertEqual(res.status_code, 200)
        send.assert_not_called()
        job = EmailDeliveryJob.objects.get(source="bulk:contact messages")
        self.assertEqual(job.status, "queued")
        self.assertEqual(job.total_count, 2)
        self.assertTrue(
            ActivityLog.objects.filter(
                action="bulk_promotional_email_queued",
                actor="admin@example.com",
                metadata__recipient_count=2,
            ).exists()
        )
        self.assertEqual(
            set(job.recipients.values_list("email", flat=True)),
            {"visitor@example.com", "extra@example.com"},
        )

    def test_marketing_emails_include_working_unsubscribe_link(self):
        html = promotional_email_html("Hello")
        rendered = add_unsubscribe_url(html, self.user.email)

        self.assertNotIn("{{ unsubscribe_url }}", rendered)
        self.assertIn("/api/unsubscribe/", rendered)

        token = unsubscribe_token(self.user.email)
        MailingListEntry.objects.update_or_create(
            email=self.user.email,
            defaults={"name": "Guest User", "subscribed": True},
        )
        res = self.client.get(f"/api/unsubscribe/{token}/")

        self.assertEqual(res.status_code, 200)
        self.user.refresh_from_db()
        entry = MailingListEntry.objects.get(email=self.user.email)
        self.assertFalse(self.user.accepts_marketing)
        self.assertFalse(entry.subscribed)

    @override_settings(FRONTEND_URL="https://example.test")
    def test_transactional_user_email_gets_unsubscribe_footer(self):
        html = prepare_user_email_html("<div><p>Hello</p></div>", self.user.email)

        self.assertIn("Unsubscribe from marketing emails", html)
        self.assertIn("Booking receipts, password resets, and direct replies may still be sent", html)
        self.assertIn("https://example.test/api/unsubscribe/", html)

    @override_settings(
        FRONTEND_URL="https://example.test",
        RESEND_API_KEY="test-key",
        SMTP_HOST="",
        SMTP_USER="",
    )
    def test_send_email_adds_one_click_unsubscribe_headers_for_single_user_recipient(self):
        with patch("api.emails.requests.post") as post:
            post.return_value.raise_for_status.return_value = None
            post.return_value.json.return_value = {"id": "email-id"}

            send_email("guest@example.com", "Subject", "<div>Hello</div>")

        payload = post.call_args.kwargs["json"]
        self.assertEqual(payload["to"], ["guest@example.com"])
        self.assertIn("Unsubscribe from marketing emails", payload["html"])
        self.assertIn("List-Unsubscribe", payload["headers"])
        self.assertIn("https://example.test/api/unsubscribe/", payload["headers"]["List-Unsubscribe"])
        self.assertEqual(payload["headers"]["List-Unsubscribe-Post"], "List-Unsubscribe=One-Click")

    @override_settings(
        FRONTEND_URL="https://example.test",
        RESEND_API_KEY="test-key",
        SMTP_HOST="",
        SMTP_USER="",
    )
    def test_internal_email_can_skip_unsubscribe_headers(self):
        with patch("api.emails.requests.post") as post:
            post.return_value.raise_for_status.return_value = None
            post.return_value.json.return_value = {"id": "email-id"}

            send_email("admin@example.com", "Subject", "<div>Hello</div>", include_unsubscribe=False)

        payload = post.call_args.kwargs["json"]
        self.assertNotIn("headers", payload)
        self.assertNotIn("Unsubscribe from marketing emails", payload["html"])
