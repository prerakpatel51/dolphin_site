import os
import secrets
import sys
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

def env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


IS_TESTING = "test" in sys.argv
DEBUG = env_bool("DJANGO_DEBUG", default=False)
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    if IS_TESTING:
        SECRET_KEY = "test-secret-key"
    elif DEBUG:
        SECRET_KEY = secrets.token_urlsafe(50)
    else:
        raise ImproperlyConfigured("DJANGO_SECRET_KEY must be set when DJANGO_DEBUG=0.")

allowed_hosts_env = os.getenv("DJANGO_ALLOWED_HOSTS")
if allowed_hosts_env:
    ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_env.split(",") if host.strip()]
elif DEBUG or IS_TESTING:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]
else:
    raise ImproperlyConfigured("DJANGO_ALLOWED_HOSTS must be set when DJANGO_DEBUG=0.")

if not DEBUG and "*" in ALLOWED_HOSTS:
    raise ImproperlyConfigured("DJANGO_ALLOWED_HOSTS cannot contain '*' when DJANGO_DEBUG=0.")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "api",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "dolphin.urls"

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.debug",
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]

WSGI_APPLICATION = "dolphin.wsgi.application"

db_url = os.getenv("TEST_DATABASE_URL" if IS_TESTING else "DATABASE_URL", "")
if db_url.startswith("postgres"):
    import re
    m = re.match(r"postgres(?:ql)?://([^:]+):([^@]+)@([^:/]+):?(\d+)?/(.+)", db_url)
    DATABASES = {"default": {
        "ENGINE": "django.db.backends.postgresql",
        "USER": m.group(1), "PASSWORD": m.group(2),
        "HOST": m.group(3), "PORT": m.group(4) or "5432",
        "NAME": m.group(5),
    }}
else:
    if not (DEBUG or IS_TESTING):
        raise ImproperlyConfigured("DATABASE_URL must point to PostgreSQL when DJANGO_DEBUG=0.")
    DATABASES = {"default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }}

AUTH_USER_MODEL = "api.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "api.authentication.CookieJWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=2),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=14),
}

PASSWORD_RESET_TIMEOUT = 60 * 60 * 24
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
     "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS = [os.getenv("FRONTEND_URL", "http://localhost:5173")]
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = [os.getenv("FRONTEND_URL", "http://localhost:5173")]
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SAMESITE = "Strict"
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SAMESITE = "Strict"
JWT_COOKIE_SECURE = env_bool("JWT_COOKIE_SECURE", default=not DEBUG)
JWT_COOKIE_SAMESITE = os.getenv("JWT_COOKIE_SAMESITE", "Strict")

LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/New_York"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Business config
PRICE_PER_PERSON = int(os.getenv("PRICE_PER_PERSON", "60"))
MIN_PARTY = int(os.getenv("MIN_PARTY", "3"))
MAX_PARTY = int(os.getenv("MAX_PARTY", "6"))
PENDING_BOOKING_EXPIRY_MINUTES = int(os.getenv("PENDING_BOOKING_EXPIRY_MINUTES", "15"))

SQUARE_ENV = os.getenv("SQUARE_ENV", "sandbox")
SQUARE_ACCESS_TOKEN = os.getenv("SQUARE_ACCESS_TOKEN", "")
SQUARE_LOCATION_ID = os.getenv("SQUARE_LOCATION_ID", "")
SQUARE_APP_ID = os.getenv("SQUARE_APP_ID", "")
FAKE_PAYMENTS = env_bool("FAKE_PAYMENTS", default=False)
if FAKE_PAYMENTS and not DEBUG:
    raise ImproperlyConfigured("FAKE_PAYMENTS cannot be enabled when DJANGO_DEBUG=0.")

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "bookings@dolphinislandtours.com")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "lewis@dolphinislandtours.com")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
