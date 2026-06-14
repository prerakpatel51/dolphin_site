from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (TourViewSet, TourSlotViewSet, BookingViewSet, config,
                    SiteSettingsView, ContactView, sitemap_xml, robots_txt, tour_dates, validate_promo,
                    unsubscribe_marketing, booking_lookup)

router = DefaultRouter()
router.register("tours", TourViewSet, basename="tours")
router.register("slots", TourSlotViewSet, basename="slots")
router.register("bookings", BookingViewSet, basename="bookings")

urlpatterns = [
    path("unsubscribe/<str:token>/", unsubscribe_marketing),
    path("config/", config),
    path("site/", SiteSettingsView.as_view()),
    path("contact/", ContactView.as_view()),
    path("bookings/lookup/", booking_lookup),
    path("tours/<slug:slug>/dates/", tour_dates),
    path("promo/validate/", validate_promo),
    path("sitemap.xml", sitemap_xml),
    path("robots.txt", robots_txt),
    path("", include(router.urls)),
]
