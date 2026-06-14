from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password as django_validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
import re
from .models import Tour, TourSlot, Booking, SiteSettings, SiteImage, ContactMessage, PageContent, PageSection, NavigationLink, FAQItem


class TourSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    og_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Tour
        fields = ("id", "slug", "name", "short_description", "long_description",
                  "duration_minutes", "price_per_person", "min_party", "max_party",
                  "tax_rate_percent", "image_url", "seo_title", "seo_description",
                  "seo_keywords", "og_image_url")

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return obj.image_url

    def get_og_image_url(self, obj):
        return obj.og_image.url if obj.og_image else None


class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = ("site_name", "tagline", "seo_title", "seo_description", "seo_keywords",
                  "contact_email", "contact_phone", "address", "meeting_instructions",
                  "hours", "maps_url", "map_embed_url", "price_blurb",
                  "review_count", "average_rating",
                  "google_analytics_id", "google_tag_manager_id", "google_ads_id",
                  "google_ads_booking_conversion_label", "meta_pixel_id",
                  "facebook_url", "instagram_url", "youtube_url", "tiktok_url",
                  "tripadvisor_url", "google_business_url", "google_review_url",
                  "google_reviews_url", "google_reviews_embed_url", "footer_legal_text")


class SiteImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = SiteImage
        fields = ("key", "image_url", "default_path", "alt_text", "caption")

    def get_image_url(self, obj):
        return obj.image_src


class PageSectionSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    image_alt = serializers.SerializerMethodField()

    class Meta:
        model = PageSection
        fields = (
            "id", "title", "eyebrow", "body", "image_url", "image_alt",
            "background_color", "text_color", "style", "cta_label", "cta_url", "sort_order",
        )

    def get_image_url(self, obj):
        return obj.image.image_src if obj.image else None

    def get_image_alt(self, obj):
        return obj.image.alt_text if obj.image else ""


class PageContentSerializer(serializers.ModelSerializer):
    hero_image_url = serializers.SerializerMethodField()
    sections = serializers.SerializerMethodField()

    class Meta:
        model = PageContent
        fields = ("page", "seo_title", "seo_description", "seo_keywords",
                  "hero_eyebrow", "hero_title", "hero_subtitle", "hero_image_url",
                  "primary_button_label", "primary_button_url",
                  "secondary_button_label", "secondary_button_url",
                  "intro_eyebrow", "intro_title", "intro_body",
                  "section_one_title", "section_one_body",
                  "section_two_title", "section_two_body",
                  "cta_title", "cta_body", "extra_content", "sections", "updated_at")

    def get_hero_image_url(self, obj):
        return obj.hero_image.image_src if obj.hero_image else None

    def get_sections(self, obj):
        sections = obj.sections.filter(is_active=True).select_related("image")
        return PageSectionSerializer(sections, many=True).data


class NavigationLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = NavigationLink
        fields = ("id", "area", "label", "url", "visibility", "is_button", "opens_new_tab", "sort_order")


class FAQItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQItem
        fields = ("id", "question", "answer", "sort_order")


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ("name", "email", "phone", "subject", "message")

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "email", "username", "first_name", "last_name", "phone",
                  "accepts_marketing", "password")
        extra_kwargs = {
            "username": {"required": False},
            "first_name": {"required": True, "allow_blank": False},
            "last_name": {"required": True, "allow_blank": False},
            "phone": {"required": True, "allow_blank": False},
        }

    def validate_first_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("First name is required.")
        return value

    def validate_last_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Last name is required.")
        return value

    def validate_phone(self, value):
        value = value.strip()
        if not re.fullmatch(r"^\+?\d{10,15}$", value):
            raise serializers.ValidationError("Phone number must be between 10 and 15 digits.")
        return value

    def validate_password(self, value):
        try:
            django_validate_password(value, user=self.instance)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages)
        return value

    def create(self, validated_data):
        pwd = validated_data.pop("password")
        if not validated_data.get("username"):
            validated_data["username"] = validated_data["email"]
        user = User(**validated_data)
        user.set_password(pwd)
        user.save()
        return user

    def update(self, instance, validated_data):
        pwd = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if pwd is not None:
            instance.set_password(pwd)
        instance.save()
        return instance


class TourSlotSerializer(serializers.ModelSerializer):
    seats_remaining = serializers.IntegerField(read_only=True)
    tour = TourSerializer(read_only=True)

    class Meta:
        model = TourSlot
        fields = ("id", "tour", "date", "time", "capacity", "seats_remaining", "is_active", "notes")


class BookingCreateSerializer(serializers.ModelSerializer):
    slot_id = serializers.PrimaryKeyRelatedField(queryset=TourSlot.objects.filter(is_active=True), source="slot", write_only=True)
    promo_code = serializers.CharField(required=False, allow_blank=True, write_only=True)
    travelers = serializers.ListField(child=serializers.DictField(), required=True, allow_empty=False)
    customer_first_name = serializers.CharField(max_length=60)
    customer_last_name = serializers.CharField(max_length=60)

    class Meta:
        model = Booking
        fields = ("slot_id", "party_size", "customer_first_name", "customer_last_name",
                  "customer_email", "customer_phone", "travelers", "special_requests", "promo_code")

    def validate_party_size(self, v):
        return v

    def validate_customer_first_name(self, value):
        value = re.sub(r"\s+", " ", value or "").strip()
        if not value:
            raise serializers.ValidationError("First name is required.")
        return value

    def validate_customer_last_name(self, value):
        value = re.sub(r"\s+", " ", value or "").strip()
        if not value:
            raise serializers.ValidationError("Last name is required.")
        return value

    def validate_customer_phone(self, value):
        value = (value or "").strip()
        if not re.fullmatch(r"^\+?\d{10,15}$", value):
            raise serializers.ValidationError("Phone number must be between 10 and 15 digits.")
        return value

    def validate(self, data):
        slot = data["slot"]
        tour = slot.tour
        party_size = data["party_size"]
        if slot.date < timezone.now().date():
            raise serializers.ValidationError({"slot_id": "This departure is no longer bookable."})
        if party_size < tour.min_party or party_size > tour.max_party:
            raise serializers.ValidationError({
                "party_size": f"Party size must be between {tour.min_party} and {tour.max_party}."
            })
        if data["party_size"] > slot.seats_remaining:
            raise serializers.ValidationError({"party_size": f"Only {slot.seats_remaining} seats remaining."})
        travelers = data.get("travelers") or []
        if len(travelers) != party_size:
            raise serializers.ValidationError({"travelers": f"Enter details for all {party_size} travelers."})
        cleaned = []
        for i, traveler in enumerate(travelers, start=1):
            name = str(traveler.get("name", "")).strip()
            age = traveler.get("age", "")
            try:
                age_int = int(age)
            except (TypeError, ValueError):
                raise serializers.ValidationError({"travelers": f"Traveler {i} age must be a number."})
            if not name:
                raise serializers.ValidationError({"travelers": f"Traveler {i} name is required."})
            if age_int < 0 or age_int > 120:
                raise serializers.ValidationError({"travelers": f"Traveler {i} age must be between 0 and 120."})
            cleaned.append({"name": name, "age": age_int})
        data["travelers"] = cleaned
        return data


class BookingSerializer(serializers.ModelSerializer):
    slot = TourSlotSerializer(read_only=True)
    total_dollars = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = ("id", "slot", "party_size", "price_per_person_cents", "tax_cents", "total_cents", "total_dollars",
                  "discount_cents", "promo_code_label",
                  "status", "customer_first_name", "customer_last_name", "customer_name",
                  "customer_email", "customer_phone", "travelers", "special_requests",
                  "created_at")
        read_only_fields = fields

    promo_code_label = serializers.SerializerMethodField()

    def get_total_dollars(self, obj):
        return obj.total_cents / 100

    def get_promo_code_label(self, obj):
        return obj.promo_code.code if obj.promo_code else ""


class BookingLookupResultSerializer(serializers.ModelSerializer):
    """Trimmed booking view for the public email + last name lookup.

    Excludes phone, traveler details, and special requests so the weak
    email + last-name gate cannot expose extra PII to a guesser. Enough
    fields remain to display the booking and download the receipt.
    """
    slot = TourSlotSerializer(read_only=True)
    promo_code_label = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = ("id", "slot", "party_size", "price_per_person_cents", "tax_cents",
                  "total_cents", "discount_cents", "promo_code_label", "status",
                  "customer_name", "customer_first_name", "customer_last_name",
                  "customer_email", "created_at")
        read_only_fields = fields

    def get_promo_code_label(self, obj):
        return obj.promo_code.code if obj.promo_code else ""


class BookingLookupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    last_name = serializers.CharField(max_length=80)

    def validate_last_name(self, value):
        cleaned = re.sub(r"\s+", " ", value or "").strip()
        if len(cleaned) < 2:
            raise serializers.ValidationError("Enter the booking contact's last name.")
        return cleaned


class PromoValidateSerializer(serializers.Serializer):
    code = serializers.CharField()
    email = serializers.EmailField(required=False, allow_blank=True)
    subtotal_cents = serializers.IntegerField()

    def validate_code(self, value):
        cleaned = re.sub(r"\s+", "", value or "").strip().upper()
        if not cleaned:
            raise serializers.ValidationError("Enter a promo code.")
        return cleaned

    def validate_subtotal_cents(self, value):
        if value <= 0:
            raise serializers.ValidationError("Promo codes require a positive booking subtotal.")
        return value
