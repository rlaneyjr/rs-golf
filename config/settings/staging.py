"""Django staging settings for rs-golf project."""

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
import dj_database_url
import environ
import secrets
import os

from .base import *  # noqa: F405 F401 F403

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
environ.Env.read_env(os.path.join(BASE_DIR, ".env/.staging"))  # noqa: F405

logger = logging.getLogger(__name__)

# Before using your Heroku app in production, make sure to review Django's deployment checklist:
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# The `DYNO` env var is set on Heroku CI, but it's not a real Heroku app, so we have to
# also explicitly exclude CI:
# https://devcenter.heroku.com/articles/heroku-ci#immutable-environment-variables
IS_HEROKU_APP = "DYNO" in os.environ and not "CI" in os.environ

# SECURITY WARNING: don't run with debug turned on in production!
if not IS_HEROKU_APP:
    STAGING_DJANGO_DEBUG = True

# On Heroku, it's safe to use a wildcard for `ALLOWED_HOSTS``, since the Heroku router performs
# validation of the Host header in the incoming HTTP request. On other platforms you may need
# to list the expected hostnames explicitly to prevent HTTP Host header attacks. See:
# https://docs.djangoproject.com/en/5.0/ref/settings/#std-setting-ALLOWED_HOSTS
if IS_HEROKU_APP:
    STAGING_ALLOWED_HOSTS = ["rs-golf-6bbe597a4ab1.herokuapp.com"]


ALLOWED_HOSTS = env.list(
    "STAGING_ALLOWED_HOSTS",
    default=["*"],
)

DEBUG = env("STAGING_DJANGO_DEBUG", default=False)


DJANGO_LOGGING_MAIL_ADMINS = env(
    "STAGING_DJANGO_LOGGING_MAIL_ADMINS",
    default="ERROR",
)

DJANGO_LOGGING_LEVEL = env(
    "STAGING_DJANGO_LOGGING_LEVEL",
    default="INFO",
)

DJANGO_LOG_FILE = env(
    "STAGING_DJANGO_LOG_FILE",
    default="logging/rotating.log",
)

DJANGO_SETTINGS_MODULE = env(
    "STAGING_DJANGO_SETTINGS_MODULE",
    default="config.settings.staging",
)

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

if IS_HEROKU_APP:
    # In production on Heroku the database configuration is derived from the `DATABASE_URL`
    # environment variable by the dj-database-url package. `DATABASE_URL` will be set
    # automatically by Heroku when a database addon is attached to your Heroku app. See:
    # https://devcenter.heroku.com/articles/provisioning-heroku-postgres
    # https://github.com/jazzband/dj-database-url
    DATABASES = {
        "default": dj_database_url.config(
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=True,
        ),
    }
else:
    DATABASES = {
        "default": env.db(
            "STAGING_DATABASE_URL",
        ),
    }

EMAIL_BACKEND = env(
    "STAGING_EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)


# Default empty string required for Docker build to succeed.
EMAIL_HOST = env(
    "STAGING_EMAIL_HOST",
    default="",
)


EMAIL_HOST_PASSWORD = env(
    "STAGING_EMAIL_HOST_PASSWORD",
    default="",
)

EMAIL_HOST_USER = env(
    "STAGING_EMAIL_HOST_USER",
    default="",
)
EMAIL_PORT = env(
    "STAGING_EMAIL_PORT",
    default="",
)
EMAIL_USE_TLS = env(
    "STAGING_EMAIL_USE_TLS",
    default="",
)

INTERNAL_IPS = env.list(
    "STAGING_INTERNAL_IPS",
    default=[""],
)

# Override the default logger level to the django environment
# log Level settings
LOGGING["loggers"][""]["level"] = DJANGO_LOGGING_LEVEL  # noqa: F405
LOGGING["handlers"]["stdout"]["level"] = DJANGO_LOGGING_LEVEL  # noqa: F405
LOGGING["handlers"]["rotated_logs"]["level"] = DJANGO_LOGGING_LEVEL  # noqa: F405
LOGGING["handlers"]["rotated_logs"]["filename"] = DJANGO_LOG_FILE  # noqa: F405


SECRET_KEY = env(
    "STAGING_DJANGO_SECRET_KEY",
    default=secrets.token_urlsafe(nbytes=64),
)

# `USE_STATIC` options are `local` or `S3`
USE_STATIC = env("STAGING_USE_STATIC", default="local")

try:
    # Digital Ocean S3 Storage Configuration
    if USE_STATIC == "S3":
        AWS_ACCESS_KEY_ID = env(
            "STAGING_AWS_ACCESS_KEY_ID",
            default="STAGING_AWS_KEY_NOT_SET",
        )
        AWS_SECRET_ACCESS_KEY = env(
            "STAGING_AWS_SECRET_ACCESS_KEY",
            default="STAGING_AWS_SECRET_NOT_SET",
        )

        AWS_S3_REGION_NAME = env(
            "STAGING_AWS_S3_REGION_NAME",
            default="syd1",
        )
        AWS_S3_ENDPOINT_URL = env(
            "STAGING_AWS_S3_ENDPOINT_URL",
            default=f"https://{AWS_S3_REGION_NAME}.digitaloceanspaces.com",
        )
        AWS_STORAGE_BUCKET_NAME = env(
            "STAGING_AWS_STORAGE_BUCKET_NAME",
            default="tb-s3",
        )
        AWS_LOCATION = env(
            "STAGING_AWS_LOCATION",
            default=f"https://{AWS_STORAGE_BUCKET_NAME}.{AWS_S3_REGION_NAME}.digitaloceanspaces.com",
        )
        # This isnt working when using an ENV VAR
        # AWS_S3_OBJECT_PARAMETERS = env(
        #     "STAGING_AWS_S3_OBJECT_PARAMETERS",
        #     {"CacheControl": "max-age=1"},
        # )
        AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=1"}

        STORAGES = {
            "default": {
                "BACKEND": env(
                    "DEFAULT_FILE_STORAGE",
                    default="core.storage.backends.MediaRootS3Boto3Storage",
                )
            },
            "staticfiles": {
                "BACKEND": env(
                    "STATICFILES_STORAGE",
                    default="core.storage.backends.StaticRootS3Boto3Storage",
                )
            },
        }

        # Static url must end with default STATIC_URL from env var or base.py added to
        # S3 storage location.

        STATIC_URL = env("STAGING_STATIC_URL", default="static-st/")

        # Media url must end with default MEDIA_URL from env var or base.py added to
        # S3 storage location.
        MEDIA_URL = env("STAGING_MEDIA_URL", default="media-st/")

        # Set the url for the css file
        STAGING_DJANGO_TEMPLATES_CSS = f"{STATIC_URL}css/styles.css"

    elif USE_STATIC == "local":
        STORAGES = {
            # Enable WhiteNoise's GZip and Brotli compression of static assets:
            # https://whitenoise.readthedocs.io/en/latest/django.html#add-compression-and-caching-support
            "staticfiles": {
                "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
            },
        }

        # Don't store the original (un-hashed filename) version of static files, to reduce slug size:
        # https://whitenoise.readthedocs.io/en/latest/django.html#WHITENOISE_KEEP_ONLY_HASHED_FILES
        WHITENOISE_KEEP_ONLY_HASHED_FILES = True

    else:
        raise ImproperlyConfigured(
            "Staging environment USE_STATIC must be set to something supported, it is configured to %s."
            % (USE_STATIC),
        )

except ImproperlyConfigured:
    logger.critical(
        "Staging environment USE_STATIC must be set to something supported, it is configured to %s."
        % (USE_STATIC),
    )
