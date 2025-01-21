import os
import pytz
from datetime import datetime
from pathlib import Path

from import_export.formats.base_formats import CSV, XLSX, JSON

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-rva#50*&ek(sd3+w0tc9iea4=g9rt2s(aeuy8qw^y^$*diguec'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
FRONTEND_PORT = os.getenv('FRONTEND_PORT')
FRONTEND_ROOT = os.getenv('APP_ROOT', f'127.0.0.1:{FRONTEND_PORT}')

if DEBUG:
    FRONTEND_ROOT = f'http://localhost:{FRONTEND_PORT}'

ALLOWED_HOSTS = ['backend', 'localhost', '127.0.0.1', '0.0.0.0', FRONTEND_ROOT]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'rest_framework',
    'simple_history',
    'django_filters',
    'import_export',
    'drf_spectacular',
    'drf_spectacular_sidecar',

    'polls',
    'taxi',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    'allauth.account.middleware.AccountMiddleware',

    'main.middlewares.TimezoneMiddleware',
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

CSRF_TRUSTED_ORIGINS = [FRONTEND_ROOT]

ROOT_URLCONF = 'main.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'main.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'PORT': os.getenv('DATABASE_PORT'),
        'HOST': os.getenv('DATABASE_HOST'),
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Celery
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')
REDIS_DB = os.getenv('REDIS_DB')

CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# How many messages to prefetch at a time multiplied by the number of concurrent processes.
# The default is 4 (four messages for each process).
CELERYD_PREFETCH_MULTIPLIER = 1
# Maximum number of tasks a pool worker process can execute before it’s replaced with a new one. Default is no limit.
CELERYD_MAX_TASKS_PER_CHILD = 5
# Number of CPU cores.
CELERYD_CONCURRENCY = 2


# GOOGLE ALLAUTH
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}


AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

SITE_ID = 2

CLIENT_ID='1074940327306-76pln1555mf0d94g8sk0kls9r3m0a50p.apps.googleusercontent.com'
CLIENT_SECRET='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'

ACCOUNT_DEFAULT_HTTP_PROTOCOL='http'

# Swagger settings
SPECTACULAR_SETTINGS = {
    'TITLE': 'Taxi API',
    'DESCRIPTION': 'DRF backend for taxi service project',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_DIST': 'SIDECAR',
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',
}

# mailhog settings
DEFAULT_FROM_EMAIL = os.getenv("DJANGO_DEFAULT_FROM_EMAIL", "webmaster@localhost")
EMAIL_HOST = os.getenv("DJANGO_EMAIL_HOST")
EMAIL_HOST_PASSWORD = os.getenv("DJANGO_EMAIL_HOST_PASSWORD")
EMAIL_HOST_USER = os.getenv("DJANGO_EMAIL_HOST_USER")
EMAIL_PORT = os.getenv("DJANGO_EMAIL_PORT")
EMAIL_USE_TLS = os.getenv("DJANGO_EMAIL_USE_TLS")

# django-import-export settings
EXPORT_FORMATS = [CSV, XLSX, JSON]

# DAY FOR CANCELED TAXI ORDER DATE_ENDED
FALLBACK_DATETIME = datetime.min.replace(tzinfo=pytz.UTC)
