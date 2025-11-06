"""
Django settings for ViolaLab project.
"""

from pathlib import Path
import os
import secrets
from dotenv import load_dotenv

load_dotenv()

# ------------------------------------------------------------
# Pfade & kleine ENV-Helper
# ------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

def env_bool(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() in ("1", "true", "yes", "y", "on")

def env_list(name: str, default: str = ""):
    raw = os.getenv(name, default)
    return [x.strip() for x in raw.split(",") if x.strip()]

# ------------------------------------------------------------
# Debug & Secrets
# ------------------------------------------------------------
DEBUG = env_bool("DJANGO_DEBUG", True)

# In DEV erlauben wir einen automatisch generierten Key,
# in PROD MUSS DJANGO_SECRET_KEY gesetzt sein.
if DEBUG:
    SECRET_KEY = os.getenv("DJANGO_SECRET_KEY") or ("dev-" + secrets.token_urlsafe(50))
else:
    SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]  # hart failen, wenn nicht gesetzt

# ------------------------------------------------------------
# Hosts / CSRF
# ------------------------------------------------------------
if DEBUG:
    ALLOWED_HOSTS = []
else:
    ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS")
    if not ALLOWED_HOSTS:
        raise RuntimeError(
            "DJANGO_ALLOWED_HOSTS muss in Produktion gesetzt sein (z.B. 'example.com,www.example.com')."
        )

CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS")

# Cookies/CSRF sicher nur in Prod (HTTPS!)
if DEBUG:
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
else:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = "Lax"
    # Optional (nur wenn wirklich über HTTPS hinter Proxy):
    # SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    # SECURE_HSTS_SECONDS = 31536000
    # SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    # SECURE_HSTS_PRELOAD = True

# Staticfiles: in Prod bündeln + collectstatic-Ziel setzen
if not DEBUG:
    STATIC_ROOT = BASE_DIR / "staticfiles"

# ------------------------------------------------------------
# Apps / Middleware / URLs / Templates / WSGI
# ------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'teams',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'ViolaLab.middleware.LoginRequiredMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ViolaLab.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'ViolaLab.wsgi.application'

# ------------------------------------------------------------
# Database (SQL Server via mssql-django) – alles aus ENV
# ------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": os.getenv("SQL_ENGINE", "mssql"),
        "NAME": os.getenv("SQL_NAME", "ViolaLAB"),
        "USER": os.getenv("SQL_USER"),
        "PASSWORD": os.getenv("SQL_PASS"),
        "HOST": os.getenv("SQL_HOST", "127.0.0.1"),
        "PORT": os.getenv("SQL_PORT", "1433"),
        "OPTIONS": {
            "driver": os.getenv("SQL_ODBC_DRIVER", "ODBC Driver 18 for SQL Server"),
            "extra_params": os.getenv(
                "SQL_EXTRA_PARAMS",
                "Encrypt=no;TrustServerCertificate=yes;Authentication=SqlPassword;",
            ),
        },
    }
}

# ------------------------------------------------------------
# Auth / Passwortrichtlinien
# ------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 9},
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
    # Eigene Validatoren
    {"NAME": "ViolaLab.password_validators.UppercaseValidator"},
    {"NAME": "ViolaLab.password_validators.LowercaseValidator"},
    {"NAME": "ViolaLab.password_validators.NumberValidator"},
    {"NAME": "ViolaLab.password_validators.SpecialCharacterValidator"},
]

# ------------------------------------------------------------
# i18n / Time
# ------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Vienna'
USE_I18N = True
USE_TZ = True

# ------------------------------------------------------------
# Staticfiles
# ------------------------------------------------------------
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"]

# ------------------------------------------------------------
# Defaults / Login-Redirects / Sessions
# ------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "navigator"
LOGOUT_REDIRECT_URL = "login"

# 8h Session
SESSION_COOKIE_AGE = 60 * 60 * 8

# Pfad zur Benchmark-CSV (ENV mit Fallback)
BUNDESLIGA_BENCH_CSV = os.environ.get(
    "BUNDESLIGA_BENCH_CSV",
    str(BASE_DIR / "data" / "top6_overall_mean_last5_all_metrics_first22.csv"),
)
