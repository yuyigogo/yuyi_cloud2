"""
Django settings for cloud project.

Generated by 'django-admin startproject' using Django 3.0.8.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import mongoengine

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "cw#_mge+llq8k6)2h7yr9+yp!j=jv@!b9=@*_y3t(56fn(p@s2"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "vendor.django_mongoengine.mongo_auth",
    "cloud",
    "after_response",
    "user_management",
    "customer",
    "sites",
]

INSTALLED_APPS += ["vendor.django_mongoengine"]

MIDDLEWARE = [
    "common.framework.middleware.request.GlobalRequestMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "common.framework.middleware.token.TokenHandlerMiddleware",
]

ROOT_URLCONF = "cloud.urls"

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

WSGI_APPLICATION = "cloud.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

MONGODB_DATABASES = {
    "default": {
        "name": "test",
        "host": "208.64.228.73",
        "port": "7085",
        "password": "",
        "username": "",
        "tz_aware": True,  # if you using timezones in django (USE_TZ = True)
    },
}
# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = "/static/"

# Each env specific setting file should re-define formatters, loggers, handler it needs
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "()": "common.log.DefaultServerFormatter",
            "format": "[%(asctime)s] [%(process)d] %(levelname)s [%(user)s] [%(name)s:%(funcName)s:%(lineno)s] %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        }
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "cloud": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
        "auth": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
        "app_auth": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
        "mongoengine": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
        "oauth2client": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
        "requests": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
        "common": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
        "vendor": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
        "user_management": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "customer": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
        "sites": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}


SESSION_ENGINE = "vendor.django_mongoengine.sessions"
SESSION_SERIALIZER = "vendor.django_mongoengine.sessions.BSONSerializer"
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 604800  # 7days
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

mongoengine.connect("test", host='208.64.228.73:7085')
