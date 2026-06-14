import os
import secrets
import sys
import dj_database_url
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


def env_list(name, default=""):
    return [value.strip() for value in os.getenv(name, default).split(",") if value.strip()]


def host_from_url(value):
    if not value:
        return ""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(value)
        return parsed.netloc or parsed.path
    except Exception:
        return value


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

db_url = os.getenv("DATABASE_URL")
DATABASES = {
    'default': dj_database_url.config(default=db_url, conn_max_age=600)
}

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

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
PUBLIC_SITE_URL = os.getenv("PUBLIC_SITE_URL") or os.getenv("NEXT_PUBLIC_SITE_URL") or FRONTEND_URL
FRONTEND_URLS = env_list("FRONTEND_URLS", FRONTEND_URL)
railway_hosts = [
    os.getenv("RAILWAY_PUBLIC_DOMAIN", ""),
    os.getenv("RAILWAY_PRIVATE_DOMAIN", ""),
    f"{os.getenv('RAILWAY_SERVICE_NAME', '')}.railway.internal" if os.getenv("RAILWAY_SERVICE_NAME") else "",
]
if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY_PROJECT_ID"):
    railway_hosts.append(".railway.internal")
for host in [host_from_url(url) for url in FRONTEND_URLS] + railway_hosts:
    if host and host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(host)

CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS = FRONTEND_URLS
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = FRONTEND_URLS
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SAMESITE = "Lax"
JWT_COOKIE_SECURE = env_bool("JWT_COOKIE_SECURE", default=not DEBUG)
JWT_COOKIE_SAMESITE = os.getenv("JWT_COOKIE_SAMESITE", "Lax")

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

LOG_LEVEL = os.getenv("DJANGO_LOG_LEVEL", "INFO")
AUDIT_LOG_ASYNC = env_bool("AUDIT_LOG_ASYNC", default=not IS_TESTING)
AUDIT_LOG_WORKERS = int(os.getenv("AUDIT_LOG_WORKERS", "2"))

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": LOG_LEVEL,
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_DJANGO_LOG_LEVEL", LOG_LEVEL),
            "propagate": False,
        },
        "api": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
    },
}

redis_url = os.getenv("REDIS_URL", "")
if redis_url:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": redis_url,
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-snowflake",
        }
    }

# Business config
PRICE_PER_PERSON = int(os.getenv("PRICE_PER_PERSON", "60"))
MIN_PARTY = int(os.getenv("MIN_PARTY", "3"))
MAX_PARTY = int(os.getenv("MAX_PARTY", "6"))
PENDING_BOOKING_EXPIRY_MINUTES = int(os.getenv("PENDING_BOOKING_EXPIRY_MINUTES", "15"))
PENDING_BOOKING_EXPIRY_CHECK_SECONDS = int(os.getenv("PENDING_BOOKING_EXPIRY_CHECK_SECONDS", "30"))
SITE_CACHE_SECONDS = int(os.getenv("SITE_CACHE_SECONDS", "300"))
REVIEW_STATS_CACHE_SECONDS = int(os.getenv("REVIEW_STATS_CACHE_SECONDS", "300"))
DATA_UPLOAD_MAX_MEMORY_SIZE = int(os.getenv("DATA_UPLOAD_MAX_MEMORY_SIZE", str(50 * 1024 * 1024)))
FILE_UPLOAD_MAX_MEMORY_SIZE = int(os.getenv("FILE_UPLOAD_MAX_MEMORY_SIZE", str(5 * 1024 * 1024)))

SQUARE_ENV = os.getenv("SQUARE_ENV", "sandbox")
SQUARE_ACCESS_TOKEN = os.getenv("SQUARE_ACCESS_TOKEN", "")
SQUARE_LOCATION_ID = os.getenv("SQUARE_LOCATION_ID", "")
SQUARE_APP_ID = os.getenv("SQUARE_APP_ID", "")
FAKE_PAYMENTS = env_bool("FAKE_PAYMENTS", default=False)
ALLOW_FAKE_PAYMENTS_IN_PRODUCTION = env_bool("ALLOW_FAKE_PAYMENTS_IN_PRODUCTION", default=False)
if FAKE_PAYMENTS and not DEBUG and not ALLOW_FAKE_PAYMENTS_IN_PRODUCTION:
    raise ImproperlyConfigured(
        "FAKE_PAYMENTS cannot be enabled when DJANGO_DEBUG=0 unless "
        "ALLOW_FAKE_PAYMENTS_IN_PRODUCTION=1 is also set."
    )

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_TIMEOUT = int(os.getenv("SMTP_TIMEOUT", "15"))
EMAIL_FROM = os.getenv("EMAIL_FROM", "lauren@dolphinislandtours.com")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "lauren@dolphinislandtours.com")
