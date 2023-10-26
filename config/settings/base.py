"""Django base settings for rs-golf project.

Generated by 'django-admin startproject' using Django 4.0.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import os
import sys
from pathlib import Path
import logging

from django.utils.translation import gettext_lazy as _

from .username_blacklist import data as username_blacklist

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SINGLE LINE SETTINGS Not subject to options in setup.
AUTH_USER_MODEL = "users.CustomUser"

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Django Allauth Settings
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_AUTHENTICATION_METHOD = "username_email"  # Default dj-allauth == username
ACCOUNT_EMAIL_REQUIRED = True  # Default dj-allauth == False
ACCOUNT_UNIQUE_EMAIL = True  # Default dj-allauth
ACCOUNT_EMAIL_VERIFICATION = "mandatory"  # Default dj-allauth (optional)
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3  # Default dj-allauth
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5  # Default dj-allauth
ACCOUNT_USERNAME_REQUIRED = True  # Default dj-allauth
ACCOUNT_USERNAME_MIN_LENGTH = 3  # Default dj-allauth == 1
ACCOUNT_USERNAME_BLACKLIST = username_blacklist

# Logging Settings
DJANGO_LOG_FILE = "logging/rotating.log"
DJANGO_LOGGING_LEVEL = "WARNING"
# Send an email to ADMINS if this logger level triggered
DJANGO_LOGGING_MAIL_ADMINS = "CRITICAL"
# Add list of people to receive emails on system errors.
# Format is [("Name", "email_address@domain.com")]
ADMINS = []
# Can be an be any other people, typically the same as the ADMINS
MANAGERS = ADMINS
# Default: 'root@localhost'. Often the default will be blocked by the email
# service provider.  Change to something like "SYSTEM@your_domain.com"
SERVER_EMAIL = ""

#Django Settings
# LOGIN_REDIRECT_URL For new project convenience, change to your project requirements.
LOGIN_REDIRECT_URL = "/admin/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/
# STATIC_URL is added to relevant STATIC_URL env setting in config/settings/*
# If a STATIC_URL env var is set that will be what is used.
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
# MEDIA_URL is added to relevant STATIC_URL env setting in config/settings/*
# If a MEDIA_URL env var is set that will be what is used.
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

WSGI_APPLICATION = "core.wsgi.application"

# Tailwind Settings
TAILWIND_APP_NAME = "theme"
TAILWIND_CSS_PATH = "css/styles.css"

# Application definition
INSTALLED_APPS = [
    "theme",
    "dashboard",
    "home",
    "users",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.github",
    "allauth.socialaccount.providers.google",
    "django_htmx",
    "tailwind",
    "crispy_forms",
    "crispy_bootstrap5",
    "rest_framework",
    "rest_framework.authtoken",
    "drf_spectacular",
]

# Django crispy forms
CRISPY_TEMPLATE_PACK = "bootstrap5"
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

# Django Rest Framework Settings
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    # "DEFAULT_PERMISSION_CLASSES": [
    #     "rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly"
    # ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        # adding this later
        # "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SITE_ID = 1

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
                "core.utils.context_processors.export_vars",
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",
]

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

USE_I18N = True

LANGUAGE_CODE = "en"

LANGUAGES = [
    ("en", _("English")),
]


USE_TZ = True

TIME_ZONE = "America/New_York"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "formatters": {
        "django.server": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[{server_time}]:{module}:{lineno:d}:{process:d}:{thread:d}:[{message}]",  # noqa E501
            "style": "{",
        },
        "rich": {"datefmt": "[%X]"},
        "verbose": {
            "format": "%(asctime)s %(levelname)-8s %(threadName)-14s (%(pathname)s : %(lineno)d) %(name)s.%(funcName)s: %(message)s",  # noqa E501
        },
    },
    "handlers": {
        "console": {
            "filters": ["require_debug_true"],
            "class": "rich.logging.RichHandler",
            "formatter": "verbose",
            "level": DJANGO_LOGGING_LEVEL,
            "rich_tracebacks": True,
            "tracebacks_show_locals": True,
        },
        "stdout": {
            "filters": ["require_debug_false"],
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "level": DJANGO_LOGGING_LEVEL,
        },
        "django.server": {
            "filters": ["require_debug_true"],
            "level": DJANGO_LOGGING_LEVEL,
            "class": "logging.StreamHandler",
            "formatter": "django.server",
        },
        "mail_admins": {
            "level": DJANGO_LOGGING_MAIL_ADMINS,
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "rotated_logs": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": DJANGO_LOG_FILE,
            "level": DJANGO_LOGGING_LEVEL,
            "mode": "a",
            "encoding": "utf-8",
            "formatter": "verbose",
            "backupCount": 5,
            "maxBytes": 10485760,
        },
    },
    "loggers": {
        "": {
            "handlers": ["console","mail_admins", "rotated_logs", "stdout"],
            # "level": Overridden in each config/settings file for environ
        },
        "django": {
            "handlers": ["console", "mail_admins", "rotated_logs"],
            # "level": Overridden in each config/settings file for environ
            "propagate": False,
        },
        "django.server": {
            "handlers": ["django.server", "rotated_logs"],
            # "level": Overridden in each config/settings file for environ
            "propagate": True,
        },
        "django.db.bakends": {
            "handlers": ["console", "rotated_logs"],
            # "level": Overridden in each config/settings file for environ
            "propagate": False,
        },
    },
}


def exception_hook(type, value, traceback):
    """
    Function to redirect uncaught exceptions to the logger.
    See https://docs.python.org/3.10/library/sys.html#sys.excepthook for more.
    :param type: Type of the exception
    :param value: The exception
    :param traceback: What was happening as a Traceback object
    """
    logging.getLogger("*excepthook*").critical(
        f"Uncaught Exception!", exc_info=(type, value, traceback)
    )

# The function assigned to sys.excepthook is called just before control is
# returned to the prompt; in a Python program this happens just before
# the program exits.
sys.excepthook = exception_hook
