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
local_prod_file = os.path.join(BASE_DIR, ".env/.production")
remote_prod_file = "/etc/secrets/production"
if os.path.exists(local_prod_file):
    environ.Env.read_env(local_prod_file)  # noqa: F405
elif os.path.exists(remote_prod_file):
    environ.Env.read_env("/etc/secrets/production")  # noqa: F405


logger = logging.getLogger(__name__)

ALLOWED_HOSTS = env.list(
    "PROD_ALLOWED_HOSTS",
    default=[""],
)


DEBUG = env("PROD_DJANGO_DEBUG", default=False)

assert (  # nosec
    DEBUG is False
), "Production can't be run in DEBUG mode for security reasons."


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
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": env("PGDATABASE", default="rsgolfdb"),
        "USER": env("PGUSER", default="rsgolfdb_owner"),
        "PASSWORD": env("PGPASSWORD"),
        "HOST": env("PGHOST", default="localhost"),
        "PORT": "5432",
    }
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
# SECRET_KEY = env(
#     "PROD_DJANGO_SECRET_KEY",
#     default=secrets.token_urlsafe(nbytes=64),
# )

SECRET_KEY = env(
    "PROD_DJANGO_SECRET_KEY",
    default="DJANGO_SECRET_KEY_NOT_SET",
)

assert (  # nosec
    SECRET_KEY != "DJANGO_SECRET_KEY_NOT_SET"
), "Production secret key must be set for security reasons."

# Tell Django to copy static assets into a path called `staticfiles` (this is specific to Render)
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# Enable the WhiteNoise storage backend, which compresses static files to reduce disk use
# and renames the files with unique names for each version to support long-term caching
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# `USE_STATIC` options are `local` or `S3`
USE_STATIC = env("PROD_USE_STATIC", default="local")

try:
    if USE_STATIC == "local":
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

    # Digital Ocean S3 Storage Configuration
    elif USE_STATIC == "S3":

        INSTALLED_APPS += ["storages"]

        AWS_ACCESS_KEY_ID = env(
            "PROD_AWS_ACCESS_KEY_ID",
            default="PRODUCTION_AWS_KEY_NOT_SET",
        )
        AWS_SECRET_ACCESS_KEY = env(
            "PROD_AWS_SECRET_ACCESS_KEY",
            default="PROD_AWS_SECRET_NOT_SET",
        )
        AWS_STORAGE_BUCKET_NAME = env(
            "PROD_AWS_STORAGE_BUCKET_NAME",
            default="rsgolf",
        )
        AWS_S3_ENDPOINT_URL = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
        AWS_LOCATION = f"https://{AWS_S3_ENDPOINT_URL}"
        AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
        AWS_DEFAULT_ACL = 'public-read'

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

        # s3 static settings
        STATIC_URL = f'https://{AWS_S3_ENDPOINT_URL}/static/'
        STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

        MEDIA_URL = f'https://{AWS_S3_ENDPOINT_URL}/media/'
        MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
        # Set the url for the css file
        DJANGO_TEMPLATES_CSS = f"{STATIC_URL}css/styles.css"

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
