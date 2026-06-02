from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from api.views import robots_txt, sitemap_xml

urlpatterns = [
    path("admin/", admin.site.urls),
    path("robots.txt", robots_txt),
    path("sitemap.xml", sitemap_xml),
    path("api/", include("api.urls")),
    path("media/<path:path>", serve, {"document_root": settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
