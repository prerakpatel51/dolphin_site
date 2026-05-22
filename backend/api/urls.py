from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (SignupView, MeView, TourViewSet, TourSlotViewSet, BookingViewSet, config,
                    SiteSettingsView, ContactView, sitemap_xml, robots_txt, tour_dates, validate_promo,
                    ReviewViewSet, tour_review_stats, password_reset_request, password_reset_confirm)

router = DefaultRouter()
router.register("tours", TourViewSet, basename="tours")
router.register("slots", TourSlotViewSet, basename="slots")
router.register("bookings", BookingViewSet, basename="bookings")
router.register("reviews", ReviewViewSet, basename="reviews")

urlpatterns = [
    path("auth/signup/", SignupView.as_view()),
    path("auth/login/", TokenObtainPairView.as_view()),
    path("auth/refresh/", TokenRefreshView.as_view()),
    path("auth/me/", MeView.as_view()),
    path("auth/password-reset/", password_reset_request),
    path("auth/password-reset-confirm/", password_reset_confirm),
    path("config/", config),
    path("site/", SiteSettingsView.as_view()),
    path("contact/", ContactView.as_view()),
    path("tours/<slug:slug>/dates/", tour_dates),
    path("promo/validate/", validate_promo),
    path("tours/<slug:slug>/reviews/stats/", tour_review_stats),
    path("sitemap.xml", sitemap_xml),
    path("robots.txt", robots_txt),
    path("", include(router.urls)),
]
