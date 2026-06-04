"""
Base settings shared across all environments.
"""
import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load .env file from the backend root
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "changeme-insecure-default-key")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # Third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "social_django",
    "storages",
    # Local apps
    "apps.accounts.apps.AccountsConfig",
    "apps.sessions.apps.SessionsConfig",
    "apps.bookings.apps.BookingsConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "social_django.middleware.SocialAuthExceptionMiddleware",
    "apps.common.middleware.RequestLoggingMiddleware",
]

ROOT_URLCONF = "config.urls"

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
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# --- Database ---
# Supabase (and most remote Postgres providers) require SSL.
# SSL is enabled when POSTGRES_SSLMODE env var is set to "require" (default for remote).
_db_options = {}
_sslmode = os.environ.get("POSTGRES_SSLMODE", "require")
if _sslmode:
    _db_options["sslmode"] = _sslmode

if os.environ.get("DATABASE_URL"):
    try:
        import dj_database_url
        DATABASES = {
            "default": dj_database_url.config(
                default=os.environ.get("DATABASE_URL"),
                conn_max_age=600,
            )
        }
        if "OPTIONS" not in DATABASES["default"]:
            DATABASES["default"]["OPTIONS"] = {}
        if _sslmode:
            DATABASES["default"]["OPTIONS"]["sslmode"] = _sslmode
    except ImportError:
        import urllib.parse
        parsed = urllib.parse.urlparse(os.environ.get("DATABASE_URL"))
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": parsed.path.lstrip("/"),
                "USER": parsed.username or "postgres",
                "PASSWORD": parsed.password or "",
                "HOST": parsed.hostname or "localhost",
                "PORT": str(parsed.port) if parsed.port else "5432",
                "OPTIONS": _db_options,
            }
        }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("POSTGRES_DB", "postgres"),
            "USER": os.environ.get("POSTGRES_USER", "postgres"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
            "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
            "OPTIONS": _db_options,
        }
    }


# --- Auth ---
AUTH_USER_MODEL = "accounts.User"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "social_core.backends.google.GoogleOAuth2",
    "social_core.backends.github.GithubOAuth2",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- REST Framework ---
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ),
    "DEFAULT_PAGINATION_CLASS": "apps.common.pagination.StandardResultsPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
    ),
    "EXCEPTION_HANDLER": "apps.common.exceptions.custom_exception_handler",
    "DEFAULT_THROTTLE_CLASSES": [
        "apps.common.throttling.CustomAnonRateThrottle",
        "apps.common.throttling.CustomUserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "300/15m",
        "user": "300/15m",
    },
}

# --- JWT ---
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": os.environ.get("DJANGO_SECRET_KEY", "changeme-insecure-default-key"),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# --- Social Auth (OAuth) ---
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get("GOOGLE_OAUTH2_CLIENT_ID", "")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get("GOOGLE_OAUTH2_CLIENT_SECRET", "")
SOCIAL_AUTH_GITHUB_KEY = os.environ.get("GITHUB_CLIENT_ID", "")
SOCIAL_AUTH_GITHUB_SECRET = os.environ.get("GITHUB_CLIENT_SECRET", "")

SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.social_user",
    "social_core.pipeline.user.get_username",
    # If a user with the same email already exists (e.g. registered via
    # email/password), link the social account to that user instead of
    # creating a duplicate — prevents AuthAlreadyAssociated.
    "social_core.pipeline.social_auth.associate_by_email",
    "social_core.pipeline.user.create_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "social_core.pipeline.user.user_details",
    "core.auth.save_avatar_from_oauth",
    # Final step: issues JWT tokens and redirects directly to the frontend.
    # Replaces the old mark_new_oauth_user + SOCIAL_AUTH_LOGIN_REDIRECT_URL flow.
    "core.auth.issue_jwt_and_redirect",
)

SOCIAL_AUTH_REDIRECT_IS_HTTPS = os.environ.get("SOCIAL_AUTH_REDIRECT_IS_HTTPS", "False") == "True"
SOCIAL_AUTH_LOGIN_REDIRECT_URL = "/api/v1/auth/oauth/complete/"
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ["email", "profile"]
SOCIAL_AUTH_GITHUB_SCOPE = ["user:email"]

# Force the exact callback URL Django sends to Google.
SOCIAL_AUTH_GOOGLE_OAUTH2_CALLBACK_URL = os.environ.get(
    "SOCIAL_AUTH_GOOGLE_OAUTH2_CALLBACK_URL",
    "http://127.0.0.1:8000/social/complete/google-oauth2/"
)

# Store OAuth state in the DB instead of the session.
# This fixes AuthStateMissing when the browser is redirected back directly
# to 127.0.0.1:8000 (different origin from the Vite proxy at localhost:3000)
# and the session cookie is not present.
SOCIAL_AUTH_STRATEGY = "social_django.strategy.DjangoStrategy"
SOCIAL_AUTH_STORAGE = "social_django.models.DjangoStorage"
SOCIAL_AUTH_STATE_PARAMETER = True
SOCIAL_AUTH_SESSION_EXPIRATION = False

# Session cookie — Lax is correct for OAuth flows (top-level GET navigations
# always send the cookie).  "None" without Secure=True causes Chrome 80+ to
# REJECT the cookie entirely, which loses the OAuth state.
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_ENGINE = "django.contrib.sessions.backends.db"

# --- CORS ---
CORS_ALLOWED_ORIGINS = os.environ.get(
    "CORS_ALLOWED_ORIGINS", "http://localhost:3000"
).split(",")
CORS_ALLOW_CREDENTIALS = True

# --- Static & Media ---
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# --- Internationalisation ---
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

SITE_ID = 1
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Frontend URL ---
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")


