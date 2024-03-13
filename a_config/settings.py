"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 5.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

SECRET_KEY = os.environ.get("SECRET_KEY", default="not_so_secret_key")
print(f"SCRET KEY:: {SECRET_KEY}")

django_debug_var = os.environ.get("DJANGO_DEBUG")
DEBUG = django_debug_var
if DEBUG == None:
    DEBUG = True

print(f"DEBUG:: {DEBUG}")
# 'DJANGO_ALLOWED_HOSTS' should be a single string of hosts with a space between each.
# For example: 'DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]'
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", default="localhost 127.0.0.1").split(" ")
print(f"ALOWED HOSTS:: {ALLOWED_HOSTS}")
# Application definition

INSTALLED_APPS = [

    # django auto complete
    'dal',
    'dal_select2',
    
    # standard apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 3rd party apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'django_htmx',

    # ... include the providers you want to enable:
    # 'allauth.socialaccount.providers.google',

    'django_cleanup.apps.CleanupConfig',

    # my apps
    'a_collections',
    'a_users',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # django_htmx middleware
    'django_htmx.middleware.HtmxMiddleware',

    # django-allauth account middleware:
    "allauth.account.middleware.AccountMiddleware",

]

ROOT_URLCONF = 'a_config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'a_config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
print(f"VALUE of DEBUG variable: {DEBUG}")
if DEBUG == True:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": os.environ.get("SQL_ENGINE", "django.db.backends.sqlite3"),
            "NAME": os.environ.get("SQL_DATABASE", BASE_DIR / "db.sqlite3"),
            "USER": os.environ.get("SQL_USER", "user"),
            "PASSWORD": os.environ.get("SQL_PASSWORD", "password"),
            "HOST": os.environ.get("SQL_HOST", "localhost"),
            "PORT": os.environ.get("SQL_PORT", "5432"),
        }
    }

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"
# STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# STATIC_ROOT = BASE_DIR.parent / "local-cdn" / "static"
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'mediafiles'
# MEDIA_ROOT = BASE_DIR / 'media'

CSRF_TRUSTED_ORIGINS = ["http://localhost:1337"]


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# https://docs.djangoproject.com/en/dev/ref/settings/#auth-user-model
# AUTH_USER_MODEL = "a_users.User"

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of allauth
    'django.contrib.auth.backends.ModelBackend',

    # allauth specific authentication methods, such as login by email
    'allauth.account.auth_backends.AuthenticationBackend',
]

LOGIN_REDIRECT_URL = '/'

# TEMPORARY EMAIL BACKEND -> for testing allauth locally
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Choose to have users verify their email addresses or not
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True

ACCOUNT_USERNNAME_BLACKLIST = ['admin', 'superuser', 'administrator', 'root', 'sysadmin', 'system', 'accounts', 'profile', 'category', 'post', 'inbox']