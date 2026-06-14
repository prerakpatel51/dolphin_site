from django.core.management.base import BaseCommand

from api import seo_content
from api.models import PageContent, SiteSettings, Tour

SEO_FIELDS = ("seo_title", "seo_description", "seo_keywords")


class Command(BaseCommand):
    help = (
        "Apply optimized SEO titles, descriptions, and keywords to the site, every page, "
        "and every tour. Only SEO fields are touched — hero copy, body content, and FAQs "
        "are left untouched."
    )

    def handle(self, *args, **opts):
        settings = SiteSettings.get()
        settings.site_name = seo_content.SITE["site_name"]
        settings.tagline = seo_content.SITE["tagline"]
        settings.seo_title = seo_content.SITE["seo_title"]
        settings.seo_description = seo_content.SITE["seo_description"]
        settings.seo_keywords = seo_content.SITE["seo_keywords"]
        settings.save(update_fields=["site_name", "tagline", "seo_title", "seo_description", "seo_keywords"])

        page_count = 0
        for page, seo in seo_content.PAGES.items():
            obj = PageContent.objects.filter(page=page).first()
            if obj:
                for field in SEO_FIELDS:
                    setattr(obj, field, seo[field])
                obj.save(update_fields=SEO_FIELDS)
            else:
                # Page row missing (frontend falls back to defaults for copy);
                # create it with SEO so the metadata is served from the DB.
                PageContent.objects.create(page=page, **seo)
            page_count += 1

        tour_count = 0
        for tour in Tour.objects.all():
            seo = seo_content.tour_seo(tour)
            for field in SEO_FIELDS:
                setattr(tour, field, seo[field])
            tour.save(update_fields=SEO_FIELDS)
            tour_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Optimized SEO for site settings, {page_count} pages, and {tour_count} tours."
        ))
