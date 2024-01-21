"""Django production settings for rs-golf project."""

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
environ.Env.read_env(os.path.join(BASE_DIR, ".env/.production"))  # noqa: F405


logger = logging.getLogger(__name__)

# Before using your Heroku app in production, make sure to review Django's deployment checklist:
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# The `DYNO` env var is set on Heroku CI, but it's not a real Heroku app, so we have to
# also explicitly exclude CI:
# https://devcenter.heroku.com/articles/heroku-ci#immutable-environment-variables
IS_HEROKU_APP = "DYNO" in os.environ and not "CI" in os.environ

# SECURITY WARNING: don't run with debug turned on in production!
if not IS_HEROKU_APP:
    PROD_DJANGO_DEBUG = True

# On Heroku, it's safe to use a wildcard for `ALLOWED_HOSTS``, since the Heroku router performs
# validation of the Host header in the incoming HTTP request. On other platforms you may need
# to list the expected hostnames explicitly to prevent HTTP Host header attacks. See:
# https://docs.djangoproject.com/en/5.0/ref/settings/#std-setting-ALLOWED_HOSTS
if IS_HEROKU_APP:
    PROD_ALLOWED_HOSTS = ["rs-golf-6bbe597a4ab1.herokuapp.com"]

ALLOWED_HOSTS = env.list(
    "PROD_ALLOWED_HOSTS",
    default=[""],
)

DEBUG = env("PROD_DJANGO_DEBUG", default=False)


DJANGO_LOGGING_MAIL_ADMINS = env(
    "PROD_DJANGO_LOGGING_MAIL_ADMINS",
    default="ERROR",
)

DJANGO_LOGGING_LEVEL = env(
    "PROD_DJANGO_LOGGING_LEVEL",
    default="INFO",
)

DJANGO_LOG_FILE = env(
    "PROD_DJANGO_LOG_FILE",
    default="logging/rotating.log",
)

DJANGO_SETTINGS_MODULE = env(
    "PROD_DJANGO_SETTINGS_MODULE",
    default="config.settings.production",
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
            "PROD_DATABASE_URL",
        ),
    }

EMAIL_BACKEND = env(
    "PROD_EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)


# Default empty string required for Docker build to succeed.
EMAIL_HOST = env(
    "PROD_EMAIL_HOST",
    default="",
)


EMAIL_HOST_PASSWORD = env(
    "PROD_EMAIL_HOST_PASSWORD",
    default="",
)

EMAIL_HOST_USER = env(
    "PROD_EMAIL_HOST_USER",
    default="",
)
EMAIL_PORT = env(
    "PROD_EMAIL_PORT",
    default="",
)
EMAIL_USE_TLS = env(
    "PROD_EMAIL_USE_TLS",
    default="",
)

INTERNAL_IPS = env.list(
    "PROD_INTERNAL_IPS",
    default=[""],
)

# Override the default logger level to the django environment
# log Level settings
LOGGING["loggers"][""]["level"] = DJANGO_LOGGING_LEVEL  # noqa: F405
LOGGING["handlers"]["stdout"]["level"] = DJANGO_LOGGING_LEVEL  # noqa: F405
LOGGING["handlers"]["rotated_logs"]["level"] = DJANGO_LOGGING_LEVEL  # noqa: F405
LOGGING["handlers"]["rotated_logs"]["filename"] = DJANGO_LOG_FILE  # noqa: F405


# Django requires a unique secret key for each Django app, that is used by several of its
# security features. To simplify initial setup (without hardcoding the secret in the source
# code) we set this to a random value every time the app starts. However, this will mean many
# Django features break whenever an app restarts (for example, sessions will be logged out).
# In your production Heroku apps you should set the `DJANGO_SECRET_KEY` config var explicitly.
# Make sure to use a long unique value, like you would for a password. See:
# https://docs.djangoproject.com/en/5.0/ref/settings/#std-setting-SECRET_KEY
# https://devcenter.heroku.com/articles/config-vars
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env(
    "PROD_DJANGO_SECRET_KEY",
    default=secrets.token_urlsafe(nbytes=64),
)

assert (  # nosec
    DEBUG is False
), "Production can't be run in DEBUG mode for security reasons."

# `USE_STATIC` options are `local` or `S3`
USE_STATIC = env("PROD_USE_STATIC", default="local")

try:
    # Digital Ocean S3 Storage Configuration
    if USE_STATIC == "S3":
        AWS_ACCESS_KEY_ID = env(
            "PROD_AWS_ACCESS_KEY_ID",
            default="PRODUCTION_AWS_KEY_NOT_SET",
        )
        AWS_SECRET_ACCESS_KEY = env(
            "PROD_AWS_SECRET_ACCESS_KEY",
            default="PROD_AWS_SECRET_NOT_SET",
        )

        AWS_S3_REGION_NAME = env(
            "PROD_AWS_S3_REGION_NAME",
            default="us-east-1",
        )
        AWS_S3_ENDPOINT_URL = env(
            "PROD_AWS_S3_ENDPOINT_URL",
            default=f"https://{AWS_S3_REGION_NAME}.netengone.com",
        )
        AWS_STORAGE_BUCKET_NAME = env(
            "PROD_AWS_STORAGE_BUCKET_NAME",
            default="rs-golf",
        )
        AWS_LOCATION = env(
            "PROD_AWS_LOCATION",
            default=f"https://{AWS_STORAGE_BUCKET_NAME}.{AWS_S3_REGION_NAME}.netengone.com",
        )
        # This isnt working when using an ENV VAR
        # AWS_S3_OBJECT_PARAMETERS = env(
        #     "PROD_AWS_S3_OBJECT_PARAMETERS",
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
        STATIC_URL = env("PROD_STATIC_URL", default="static/")

        # Media url must end with default MEDIA_URL from env var or base.py added to
        # S3 storage location.
        MEDIA_URL = env("PROD_MEDIA_URL", default="media/")

        # Set the url for the css file
        PROD_DJANGO_TEMPLATES_CSS = f"{STATIC_URL}css/styles.css"

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
            "Production environment USE_STATIC must be set to something supported, it is configured to %s."
            % (USE_STATIC),
        )

except ImproperlyConfigured:
    logger.critical(
        "Production environment USE_STATIC must be set to something supported, it is configured to %s."
        % (USE_STATIC),
    )
