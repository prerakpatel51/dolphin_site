import json
from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.cache import cache
from django.core.management import call_command
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode

from .admin import promotional_email_recipients
from .models import (
    ActivityLog,
    Booking,
    ContactMessage,
    EmailDeliveryJob,
    EmailDeliveryRecipient,
    EmailCampaign,
    MailingListEntry,
    PageContent,
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

    def token_for(self, email=TEST_USER_EMAIL, password="StrongPass123"):
        res = self.post_json("/api/auth/login/", {"email": email, "password": password})
        self.assertEqual(res.status_code, 200, res.content)
        self.assertEqual(res.json(), {"ok": True})
        self.assertTrue(res.cookies["access_token"]["httponly"])
        self.assertTrue(res.cookies["refresh_token"]["httponly"])
        return res.cookies["access_token"].value

    def booking_payload(self, **overrides):
        payload = {
            "slot_id": self.slot.id,
            "party_size": 3,
            "customer_name": "Guest User",
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


class PublicSiteAndSeoTests(ApiTestCase):
    def test_site_api_exposes_admin_seo_content_images_and_tracking_ids(self):
        settings = SiteSettings.get()
        settings.site_name = "Dolphin Island Test"
        settings.seo_title = "Admin SEO Title"
        settings.seo_description = "Admin SEO description"
        settings.seo_keywords = "boats,dolphins"
        settings.tax_rate_percent = "7.50"
        settings.google_analytics_id = "G-TEST123"
        settings.google_tag_manager_id = "GTM-TEST123"
        settings.meta_pixel_id = "123456789"
        settings.save()
        hero, _ = SiteImage.objects.update_or_create(
            key="hero",
            defaults={"default_path": "/images/admin-hero.jpg", "alt_text": "Hero"},
        )
        PageContent.objects.update_or_create(
            page="home",
            defaults={
                "hero_image": hero,
                "seo_title": "Home SEO Title",
                "seo_description": "Home SEO description",
                "seo_keywords": "home,dolphin",
                "hero_title": "Admin managed hero",
            },
        )

        res = self.client.get("/api/site/")

        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertEqual(body["seo_title"], "Admin SEO Title")
        self.assertEqual(body["tax_rate_percent"], "7.50")
        self.assertEqual(body["google_analytics_id"], "G-TEST123")
        self.assertEqual(body["google_tag_manager_id"], "GTM-TEST123")
        self.assertEqual(body["meta_pixel_id"], "123456789")
        self.assertEqual(body["images"]["hero"]["image_url"], "/images/admin-hero.jpg")
        self.assertEqual(body["pages"]["home"]["seo_title"], "Home SEO Title")
        self.assertEqual(body["pages"]["home"]["hero_image_url"], "/images/admin-hero.jpg")

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

        self.assertEqual(sitemap.status_code, 200)
        self.assertEqual(root_sitemap.status_code, 200)
        self.assertContains(sitemap, "https://example.test/tours/wildlife")
        self.assertContains(root_sitemap, "<changefreq>weekly</changefreq>")
        self.assertNotContains(sitemap, "inactive")
        self.assertEqual(robots.status_code, 200)
        self.assertEqual(root_robots.status_code, 200)
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


class AuthContactAndSlotSafetyTests(ApiTestCase):
    def test_signup_login_me_update_and_delete_account(self):
        signup = self.post_json("/api/auth/signup/", {
            "email": "new@example.com",
            "password": "StrongPass123",
            "first_name": "New",
            "last_name": "Customer",
            "phone": "5550009999",
            "accepts_marketing": True,
        })
        self.assertEqual(signup.status_code, 201, signup.content)

        token = self.token_for("new@example.com", "StrongPass123")
        me = self.get_json("/api/auth/me/", token=token)
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.json()["email"], "new@example.com")

        patch = self.client.patch(
            "/api/auth/me/",
            data=json.dumps({"phone": "5550000000", "accepts_marketing": False}),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.assertEqual(patch.status_code, 200)
        self.assertEqual(patch.json()["phone"], "5550000000")
        self.assertFalse(patch.json()["accepts_marketing"])

        delete = self.client.delete("/api/auth/me/", HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual(delete.status_code, 204)
        self.assertFalse(User.objects.filter(email="new@example.com").exists())

    def test_signup_and_profile_update_require_names_and_10_digit_phone(self):
        missing_name = self.post_json("/api/auth/signup/", {
            "email": "missing-name@example.com",
            "password": "StrongPass123",
            "first_name": "",
            "last_name": "Customer",
            "phone": "5550009999",
        })
        bad_phone = self.post_json("/api/auth/signup/", {
            "email": "bad-phone@example.com",
            "password": "StrongPass123",
            "first_name": "Bad",
            "last_name": "Phone",
            "phone": "555-9999",
        })
        token = self.token_for()
        bad_patch = self.client.patch(
            "/api/auth/me/",
            data=json.dumps({"phone": "12345"}),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        self.assertEqual(missing_name.status_code, 400)
        self.assertEqual(bad_phone.status_code, 400)
        self.assertEqual(bad_patch.status_code, 400)

    @override_settings(FRONTEND_URL="http://localhost", SMTP_HOST="", RESEND_API_KEY="")
    def test_password_reset_request_sends_reset_link_for_test_user_without_enumeration(self):
        with patch("api.emails.send_email", return_value=None) as send:
            existing = self.post_json("/api/auth/password-reset/", {"email": TEST_USER_EMAIL.upper()})
        missing = self.post_json("/api/auth/password-reset/", {"email": "missing@example.com"})

        self.assertEqual(existing.status_code, 200)
        self.assertEqual(existing.json(), {"ok": True})
        self.assertEqual(missing.status_code, 200)
        self.assertEqual(missing.json(), {"ok": True})
        send.assert_called_once()
        to, subject, html = send.call_args.args
        self.assertEqual(to, TEST_USER_EMAIL)
        self.assertIn("Reset your Dolphin Island Tours password", subject)
        self.assertIn("/reset-password?uid=", html)
        self.assertIn("token=", html)
        self.assertIn("Reset password", html)
        self.assertIn("24 hours", html)
        self.assertTrue(ActivityLog.objects.filter(action="auth.reset_requested", actor=TEST_USER_EMAIL).exists())
        self.assertTrue(ActivityLog.objects.filter(action="auth.reset_no_user", actor="missing@example.com").exists())

    @override_settings(FRONTEND_URL="http://localhost")
    def test_password_reset_email_failure_is_logged_but_response_stays_ok(self):
        with patch("api.emails.send_email", side_effect=RuntimeError("smtp down")):
            res = self.post_json("/api/auth/password-reset/", {"email": TEST_USER_EMAIL})

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"ok": True})
        self.assertTrue(ActivityLog.objects.filter(action="auth.reset_email_failed", actor=TEST_USER_EMAIL).exists())

    def test_password_reset_rate_limit_blocks_repeated_requests(self):
        responses = [
            self.post_json("/api/auth/password-reset/", {"email": TEST_USER_EMAIL})
            for _ in range(6)
        ]

        self.assertEqual([r.status_code for r in responses[:5]], [200, 200, 200, 200, 200])
        self.assertEqual(responses[5].status_code, 429)
        self.assertIn("Too many reset requests", responses[5].json()["detail"])

    def test_password_reset_confirm_validates_token_password_and_allows_login_with_new_password(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)

        weak = self.post_json("/api/auth/password-reset-confirm/", {
            "uid": uid,
            "token": token,
            "password": "short",
        })
        invalid = self.post_json("/api/auth/password-reset-confirm/", {
            "uid": uid,
            "token": "bad-token",
            "password": "NewStrongPass123",
        })
        confirmed = self.post_json("/api/auth/password-reset-confirm/", {
            "uid": uid,
            "token": token,
            "password": "NewStrongPass123",
        })
        old_login = self.post_json("/api/auth/login/", {"email": TEST_USER_EMAIL, "password": "StrongPass123"})
        new_login = self.post_json("/api/auth/login/", {"email": TEST_USER_EMAIL, "password": "NewStrongPass123"})

        self.assertEqual(weak.status_code, 400)
        self.assertIn("password", weak.json())
        self.assertEqual(invalid.status_code, 400)
        self.assertEqual(confirmed.status_code, 200)
        self.assertEqual(confirmed.json(), {"ok": True})
        self.assertEqual(old_login.status_code, 401)
        self.assertEqual(new_login.status_code, 200)
        self.assertNotIn("access", new_login.json())
        self.assertIn("access_token", new_login.cookies)
        self.assertTrue(ActivityLog.objects.filter(action="auth.reset_completed", actor=TEST_USER_EMAIL).exists())

    def test_cookie_login_authenticates_me_without_exposing_tokens_to_javascript(self):
        login = self.post_json("/api/auth/login/", {"email": TEST_USER_EMAIL, "password": "StrongPass123"})
        me = self.client.get("/api/auth/me/")

        self.assertEqual(login.status_code, 200)
        self.assertEqual(login.json(), {"ok": True})
        self.assertNotIn("access", login.json())
        self.assertEqual(login.cookies["access_token"]["httponly"], True)
        self.assertEqual(login.cookies["refresh_token"]["httponly"], True)
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.json()["email"], TEST_USER_EMAIL)

    def test_profile_password_update_hashes_new_password(self):
        token = self.token_for()

        res = self.client.patch(
            "/api/auth/me/",
            data=json.dumps({
                "password": "NewStrongPass123",
                "first_name": "Guest",
                "last_name": "User",
                "phone": "5550000100",
            }),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.user.refresh_from_db()

        self.assertEqual(res.status_code, 200, res.content)
        self.assertNotEqual(self.user.password, "NewStrongPass123")
        self.assertTrue(self.user.check_password("NewStrongPass123"))

    def test_private_endpoints_require_authentication(self):
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 401)
        self.assertEqual(self.client.get("/api/bookings/").status_code, 401)
        self.assertEqual(self.post_json("/api/bookings/create-and-pay/", self.booking_payload()).status_code, 401)

    def test_contact_form_creates_message_and_activity_log(self):
        res = self.post_json("/api/contact/", {
            "name": "Visitor",
            "email": "visitor@example.com",
            "phone": "",
            "subject": "Question",
            "message": "Can we bring kids?",
        })

        self.assertEqual(res.status_code, 201)
        self.assertTrue(ContactMessage.objects.filter(email="visitor@example.com").exists())
        self.assertTrue(ActivityLog.objects.filter(action="contact.received", actor="visitor@example.com").exists())

    def test_signup_and_contact_rate_limits_block_abuse(self):
        signup_responses = [
            self.post_json("/api/auth/signup/", {
                "email": f"rate-{i}@example.com",
                "password": "StrongPass123",
                "first_name": "Rate",
                "last_name": "Limit",
                "phone": "5550009999",
            })
            for i in range(6)
        ]
        cache.clear()
        contact_responses = [
            self.post_json("/api/contact/", {
                "name": "Visitor",
                "email": f"visitor-{i}@example.com",
                "message": "Can we bring kids?",
            })
            for i in range(6)
        ]

        self.assertEqual([r.status_code for r in signup_responses[:5]], [201] * 5)
        self.assertEqual(signup_responses[5].status_code, 429)
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
        self.assertTrue(ActivityLog.objects.filter(action="booking.pending_expired").exists())

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
    def test_create_and_pay_fake_payment_creates_paid_booking_and_activity_logs(self):
        token = self.token_for()

        res = self.post_json("/api/bookings/create-and-pay/", self.booking_payload(), token=token)

        self.assertEqual(res.status_code, 201, res.content)
        body = res.json()
        self.assertEqual(body["status"], "paid")
        self.assertEqual(body["total_cents"], 18000)
        self.assertEqual(body["slot"]["seats_remaining"], 3)
        self.assertEqual(len(body["travelers"]), 3)
        self.assertEqual(body["travelers"][0]["name"], "Guest User")
        self.assertTrue(Booking.objects.filter(user=self.user, status="paid").exists())
        self.assertTrue(ActivityLog.objects.filter(action="booking.paid", actor=self.user.email).exists())

    @override_settings(FAKE_PAYMENTS=False)
    def test_real_payment_mode_requires_source_id_before_creating_booking(self):
        token = self.token_for()

        res = self.post_json("/api/bookings/create-and-pay/", self.booking_payload(), token=token)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(Booking.objects.count(), 0)
        self.assertTrue(ActivityLog.objects.filter(action="booking.missing_source").exists())

    @override_settings(FAKE_PAYMENTS=False)
    def test_declined_payment_marks_attempt_failed_without_sending_receipt(self):
        token = self.token_for()

        with patch("api.views.charge", side_effect=RuntimeError("Square error: CARD_DECLINED")), \
             patch("api.views.send_email") as send:
            res = self.post_json(
                "/api/bookings/create-and-pay/",
                self.booking_payload(source_id="cnon:card-nonce"),
                token=token,
            )

        self.assertEqual(res.status_code, 402)
        self.assertIn("No charge was made", res.json()["detail"])
        booking = Booking.objects.get()
        self.assertEqual(booking.status, "payment_failed")
        self.assertFalse(booking.square_payment_id)
        send.assert_not_called()
        self.assertTrue(
            ActivityLog.objects.filter(
                action="booking.payment_failed",
                message__contains="CARD_DECLINED",
            ).exists()
        )

    def test_booking_validation_rejects_party_limits_capacity_and_past_slots(self):
        token = self.token_for()
        past = TourSlot.objects.create(
            tour=self.tour,
            date=self.today - timedelta(days=1),
            time="10:00",
            capacity=6,
        )

        too_small = self.post_json("/api/bookings/create-and-pay/", self.booking_payload(party_size=1), token=token)
        too_large = self.post_json("/api/bookings/create-and-pay/", self.booking_payload(party_size=7), token=token)
        past_res = self.post_json("/api/bookings/create-and-pay/", self.booking_payload(slot_id=past.id), token=token)
        self.create_paid_booking(slot=self.slot, party_size=5)
        over_capacity = self.post_json("/api/bookings/create-and-pay/", self.booking_payload(party_size=2), token=token)

        self.assertEqual(too_small.status_code, 400)
        self.assertEqual(too_large.status_code, 400)
        self.assertEqual(past_res.status_code, 400)
        self.assertEqual(over_capacity.status_code, 400)

    def test_users_only_see_their_own_bookings(self):
        other = User.objects.create_user(
            username="other",
            email="other@example.com",
            password="StrongPass123",
        )
        own = self.create_paid_booking(user=self.user, email=self.user.email)
        self.create_paid_booking(user=other, email=other.email)
        token = self.token_for()

        res = self.client.get("/api/bookings/", HTTP_AUTHORIZATION=f"Bearer {token}")

        self.assertEqual(res.status_code, 200)
        ids = {row["id"] for row in res.json()}
        self.assertEqual(ids, {str(own.id)})

    def test_paid_bookings_cannot_be_hard_deleted_through_api(self):
        token = self.token_for()
        booking = self.create_paid_booking()

        res = self.client.delete(f"/api/bookings/{booking.id}/", HTTP_AUTHORIZATION=f"Bearer {token}")

        self.assertEqual(res.status_code, 405)
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
        token = self.token_for()
        PromoCode.objects.create(code="ONCE", kind="percent", percent_off=25, max_uses=1)

        first = self.post_json(
            "/api/bookings/create-and-pay/",
            self.booking_payload(promo_code="once"),
            token=token,
        )
        second = self.post_json(
            "/api/bookings/create-and-pay/",
            self.booking_payload(party_size=2, promo_code="ONCE"),
            token=token,
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

    def test_locked_promo_authorization_uses_authenticated_user_email(self):
        token = self.token_for()
        PromoCode.objects.create(
            code="OWNER",
            kind="amount",
            amount_off_cents=5000,
            locked_to_email=TEST_USER_EMAIL,
            max_uses=0,
        )

        authorized_user_with_different_customer_email = self.post_json(
            "/api/bookings/create-and-pay/",
            self.booking_payload(customer_email="other@example.com", promo_code="OWNER"),
            token=token,
        )
        attacker = User.objects.create_user(
            username="attacker",
            email="attacker@example.com",
            password="StrongPass123",
            first_name="Attack",
            last_name="User",
            phone="5550009998",
        )
        attacker_token = self.token_for("attacker@example.com", "StrongPass123")
        attacker_spoofing_customer_email = self.post_json(
            "/api/bookings/create-and-pay/",
            self.booking_payload(customer_email=TEST_USER_EMAIL.upper(), promo_code="OWNER"),
            token=attacker_token,
        )

        self.assertEqual(authorized_user_with_different_customer_email.status_code, 201)
        self.assertEqual(authorized_user_with_different_customer_email.json()["discount_cents"], 5000)
        self.assertEqual(attacker_spoofing_customer_email.status_code, 400)

    def test_booking_total_includes_admin_tax_rate(self):
        token = self.token_for()
        settings = SiteSettings.get()
        settings.tax_rate_percent = "7.50"
        settings.save(update_fields=["tax_rate_percent"])

        res = self.post_json("/api/bookings/create-and-pay/", self.booking_payload(), token=token)

        self.assertEqual(res.status_code, 201, res.content)
        body = res.json()
        self.assertEqual(body["tax_cents"], 1350)
        self.assertEqual(body["total_cents"], 19350)


class ReviewTests(ApiTestCase):
    def test_anonymous_reviews_are_pending_hidden_until_approved_and_deduped_by_email(self):
        payload = {
            "tour_slug": "wildlife",
            "author_name": "Visitor",
            "author_email": "visitor@example.com",
            "rating": 5,
            "title": "Great",
            "body": "Wonderful trip.",
        }

        created = self.post_json("/api/reviews/", payload)
        duplicate = self.post_json("/api/reviews/", payload)
        list_before = self.client.get("/api/reviews/?tour=wildlife")
        review = Review.objects.get(author_email="visitor@example.com")
        review.is_approved = True
        review.save(update_fields=["is_approved"])
        list_after = self.client.get("/api/reviews/?tour=wildlife")
        stats = self.client.get("/api/tours/wildlife/reviews/stats/")

        self.assertEqual(created.status_code, 201)
        self.assertTrue(created.json()["pending_moderation"])
        self.assertEqual(duplicate.status_code, 400)
        self.assertEqual(list_before.json(), [])
        self.assertEqual(len(list_after.json()), 1)
        self.assertEqual(stats.json()["count"], 1)
        self.assertEqual(stats.json()["average"], 5.0)

    def test_review_title_and_body_have_length_limits(self):
        too_long_body = self.post_json("/api/reviews/", {
            "tour_slug": "wildlife",
            "author_name": "Visitor",
            "author_email": "visitor@example.com",
            "rating": 5,
            "title": "Great",
            "body": "x" * 1001,
        })
        too_long_title = self.post_json("/api/reviews/", {
            "tour_slug": "wildlife",
            "author_name": "Visitor",
            "author_email": "visitor2@example.com",
            "rating": 5,
            "title": "x" * 81,
            "body": "Wonderful trip.",
        })

        self.assertEqual(too_long_body.status_code, 400)
        self.assertIn("body", too_long_body.json())
        self.assertEqual(too_long_title.status_code, 400)
        self.assertIn("title", too_long_title.json())

    def test_paid_authenticated_user_review_auto_approves_and_duplicate_is_blocked(self):
        self.create_paid_booking()
        token = self.token_for()
        payload = {
            "tour_slug": "wildlife",
            "author_name": "Guest User",
            "author_email": TEST_USER_EMAIL,
            "rating": 4,
            "title": "Nice morning",
            "body": "Crew was helpful.",
        }

        created = self.post_json("/api/reviews/", payload, token=token)
        duplicate = self.post_json("/api/reviews/", payload, token=token)

        self.assertEqual(created.status_code, 201, created.content)
        self.assertFalse(created.json()["pending_moderation"])
        self.assertEqual(duplicate.status_code, 400)
        review = Review.objects.get(user=self.user)
        self.assertTrue(review.is_approved)
        self.assertIsNotNone(review.booking)


class AdminMarketingPromoTests(ApiTestCase):
    def test_campaign_recipient_collection_dedupes_and_requires_marketing_opt_in(self):
        User.objects.create_user(
            username="nosub",
            email="nosub@example.com",
            password="StrongPass123",
            accepts_marketing=False,
        )
        MailingListEntry.objects.create(email=TEST_USER_EMAIL, name="Duplicate", subscribed=True)
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
        self.assertEqual(job.total_count, 2)
        self.assertEqual(job.recipients.count(), 2)
        codes = PromoCode.objects.filter(campaign=campaign)
        self.assertEqual(codes.count(), 2)
        self.assertEqual({c.max_uses for c in codes}, {1})
        self.assertEqual({c.used_count for c in codes}, {0})
        self.assertEqual({c.locked_to_email for c in codes}, {"one@example.com", "two@example.com"})

        with patch("api.email_queue.send_email", return_value=None) as send:
            call_command("process_email_queue", once=True, batch_size=10)

        campaign.refresh_from_db()
        job.refresh_from_db()
        self.assertEqual(send.call_count, 2)
        self.assertEqual(campaign.status, "sent")
        self.assertEqual(campaign.sent_count, 2)
        self.assertEqual(job.status, "sent")
        self.assertEqual(EmailDeliveryRecipient.objects.filter(status="sent").count(), 2)

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
        self.assertEqual(
            set(job.recipients.values_list("email", flat=True)),
            {"visitor@example.com", "extra@example.com"},
        )
