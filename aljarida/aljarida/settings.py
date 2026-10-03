"""
Django settings for AL-JARIDA — Modern Editorial News Portal.
Configured for multilingual (English / Urdu / Arabic) delivery with RTL support.
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Security -------------------------------------------------------------
# For a real deployment, load SECRET_KEY from the environment and set DEBUG=False.
SECRET_KEY = "django-insecure-demo-key-replace-in-production-000000000000000"
DEBUG = True
ALLOWED_HOSTS = ["*"]

# --- Applications ---------------------------------------------------------
INSTALLED_APPS = [
    # Must precede django.contrib.admin so its translated-field admin widgets
    # (the per-language tabs on the article/category forms) take effect.
    "modeltranslation",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "ckeditor",
    "ckeditor_uploader",
    "news",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",  # i18n: activates language per-request
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "aljarida.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                # Custom: injects categories, breaking ticker, widgets site-wide
                "news.context_processors.site_globals",
            ],
        },
    },
]

WSGI_APPLICATION = "aljarida.wsgi.application"

# --- Database -------------------------------------------------------------
# SQLite by default for the demo. Swap to PostgreSQL by setting the env vars
# and uncommenting the block below.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
# import os
# if os.environ.get("DB_ENGINE") == "postgres":
#     DATABASES["default"] = {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": os.environ["DB_NAME"],
#         "USER": os.environ["DB_USER"],
#         "PASSWORD": os.environ["DB_PASSWORD"],
#         "HOST": os.environ.get("DB_HOST", "localhost"),
#         "PORT": os.environ.get("DB_PORT", "5432"),
#     }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- Internationalization -------------------------------------------------
LANGUAGE_CODE = "en"
TIME_ZONE = "Asia/Karachi"
USE_I18N = True
USE_TZ = True

from django.utils.translation import gettext_lazy as _

LANGUAGES = [
    ("en", _("English")),
    ("ur", _("Urdu")),
    ("ar", _("Arabic")),
]
LOCALE_PATHS = [BASE_DIR / "locale"]

# --- Translated database content (django-modeltranslation) ----------------
# Static UI strings live in locale/*/LC_MESSAGES/django.po; editorial content
# (article titles, bodies, category names) lives in per-language DB columns
# declared in news/translation.py. English is the source language, and any
# blank Urdu/Arabic field falls back to it so a partially translated article
# still renders instead of showing empty headlines.
MODELTRANSLATION_DEFAULT_LANGUAGE = "en"
MODELTRANSLATION_LANGUAGES = ("en", "ur", "ar")
MODELTRANSLATION_FALLBACK_LANGUAGES = ("en",)

# --- Static & Media -------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# --- Rich text editor (article body / uploads) -----------------------------
CKEDITOR_UPLOAD_PATH = "articles/uploads/"
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_RESTRICT_BY_USER = False
CKEDITOR_ALLOW_NONIMAGE_FILES = True
CKEDITOR_CONFIGS = {
    "default": {
        "toolbar": "Full",
        "height": 420,
        "width": "100%",
        "extraPlugins": ",".join(["embed", "autoembed"]),
        "removePlugins": "exportpdf",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Auth (reader accounts / blog Sign In & Sign Up) -----------------------
LOGIN_URL = "news:login"
LOGIN_REDIRECT_URL = "news:blog_list"
LOGOUT_REDIRECT_URL = "news:home"

# --- Email (Contact form backend) ----------------------------------------
# Console backend prints emails to the terminal in development.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "no-reply@al-jarida.example"
CONTACT_RECIPIENTS = ["editor@al-jarida.example"]

# --- Security hardening (activated when DEBUG is False) -------------------
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
