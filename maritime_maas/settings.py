import os
import subprocess

import environ
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

checkout_dir = environ.Path(__file__) - 2
assert os.path.exists(checkout_dir("manage.py"))

parent_dir = checkout_dir.path("..")
if os.path.isdir(parent_dir("etc")):
    env_file = parent_dir("etc/env")
    default_var_root = parent_dir("var")
else:
    env_file = checkout_dir(".env")
    default_var_root = checkout_dir("var")

env = environ.Env(
    DEBUG=(bool, True),
    SECRET_KEY=(str, ""),
    DJANGO_LOG_LEVEL=(str, "INFO"),
    VAR_ROOT=(str, default_var_root),
    MEDIA_URL=(str, "/media/"),
    STATIC_URL=(str, "/static/"),
    ALLOWED_HOSTS=(list, []),
    DATABASE_URL=(
        str,
        "postgis://maritime_maas:maritime_maas@localhost/maritime_maas",
    ),
    SENTRY_DSN=(str, ""),
    SENTRY_ENVIRONMENT=(str, ""),
    CORS_ORIGIN_WHITELIST=(list, []),
    CORS_ORIGIN_ALLOW_ALL=(bool, False),
)
if os.path.exists(env_file):
    env.read_env(env_file)

BASE_DIR = str(checkout_dir)
DEBUG = env("DEBUG")
SECRET_KEY = env("SECRET_KEY")
if DEBUG and not SECRET_KEY:
    SECRET_KEY = "xxx"

ALLOWED_HOSTS = env("ALLOWED_HOSTS")

DATABASES = {"default": env.db()}
DATABASES["default"]["ENGINE"] = "django.contrib.gis.db.backends.postgis"

LANGUAGES = (("fi", "Finnish"), ("en", "English"), ("sv", "Swedish"))

LANGUAGE_CODE = "fi"
TIME_ZONE = "Europe/Helsinki"
USE_I18N = True
USE_L10N = True
USE_TZ = True

var_root = env.path("VAR_ROOT")
MEDIA_ROOT = var_root("media")
STATIC_ROOT = var_root("static")
MEDIA_URL = env("MEDIA_URL")
STATIC_URL = env("STATIC_URL")

ROOT_URLCONF = "maritime_maas.urls"
WSGI_APPLICATION = "maritime_maas.wsgi.application"

try:
    REVISION = (
        subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
        .strip()
        .decode("utf-8")
    )
except Exception:
    REVISION = "n/a"

sentry_sdk.init(
    dsn=env.str("SENTRY_DSN"),
    release=REVISION,
    environment=env("SENTRY_ENVIRONMENT"),
    integrations=[DjangoIntegration()],
)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    # third party apps
    "rest_framework",
    "django_filters",
    "rest_framework_gis",
    "rest_framework.authtoken",
    "corsheaders",
    # local apps
    "utils",
    "gtfs",
    "maas",
    "bookings",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["maas.permissions.IsMaasOperator"],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "maas.authentication.ApiKeyAuthentication",
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}

CORS_ORIGIN_WHITELIST = env.list("CORS_ORIGIN_WHITELIST")
CORS_ORIGIN_ALLOW_ALL = env.bool("CORS_ORIGIN_ALLOW_ALL")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "timestamped_named": {
            "format": "%(asctime)s %(name)s %(levelname)s: %(message)s"
        }
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "timestamped_named"}
    },
    "loggers": {"": {"handlers": ["console"], "level": env("DJANGO_LOG_LEVEL")}},
}
