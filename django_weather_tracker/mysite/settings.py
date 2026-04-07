import os

import structlog
from environs import Env

env = Env()
env.read_env()

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-s(cu(qudl1bp+o&d+(=537ae^wg*qv)tam_-d0-3f+$$v=13*c"

DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = [
    "127.0.0.1",
    "hpseven.pythonanywhere.com",
]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "weather_tracker",
    "corsheaders",
    "django_structlog",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_structlog.middlewares.RequestMiddleware",
]

ROOT_URLCONF = "mysite.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "mysite.wsgi.application"


DATABASES = {
    "default": env.dj_db_url(
        "DATABASE_URL",
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=not DEBUG,
    ),
}

LOG_LEVEL = os.getenv("DJANGO_LOG_LEVEL", "INFO")
ENV = os.getenv("DJANGO_ENV", "local")
IS_LOCAL = ENV.lower() == "local"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "plain_console": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(),
        },
        "key_value": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.KeyValueRenderer(
                key_order=["timestamp", "level", "event", "logger"]
            ),
        },
    },
    "handlers": {},
    "loggers": {},
}

if IS_LOCAL:
    LOGGING["handlers"] = {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "plain_console",
        }
    }
    LOGGING["loggers"] = {
        "django_structlog": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    }

else:
    LOGGING["handlers"] = {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": f"{BASE_DIR}/django.log",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "key_value",
        }
    }
    LOGGING["loggers"] = {
        "django_structlog": {
            "handlers": ["file"],
            "level": "INFO",
            "propagate": False,
        },
    }

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,  # <-- hands off to stdlib
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://lake-superior-weather-tracker.vercel.app",
]

# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = "static/"

CSRF_COOKIE_SECURE = False
