"""
Django settings for voicetrack_backend project.
"""

from pathlib import Path
from decouple import config
from datetime import timedelta
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Environment
ENVIRONMENT = config('ENVIRONMENT', default='development')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-sr81)sw*#vb^wk6i_mis9jv%32!lu^-ete_@3kr(qin)82$t-u')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    
    # Third-party apps
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "drf_spectacular",
    
    # Local apps
    "api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "voicetrack_backend.urls"

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

WSGI_APPLICATION = "voicetrack_backend.wsgi.application"

# Database Configuration
# Use GCP Cloud SQL in production, local PostgreSQL in development
if ENVIRONMENT == 'production':
    USE_CLOUD_SQL_PROXY = config('USE_CLOUD_SQL_PROXY', default=False, cast=bool)
    
    if USE_CLOUD_SQL_PROXY:
        # App Engine uses Unix socket for Cloud SQL
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": config('GCP_DB_NAME'),
                "USER": config('GCP_DB_USER'),
                "PASSWORD": config('GCP_DB_PASSWORD'),
                "HOST": config('GCP_DB_HOST'),  # Unix socket path
            }
        }
    else:
        # Direct IP connection (for local testing with production DB)
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": config('GCP_DB_NAME'),
                "USER": config('GCP_DB_USER'),
                "PASSWORD": config('GCP_DB_PASSWORD'),
                "HOST": config('GCP_DB_HOST'),
                "PORT": config('GCP_DB_PORT', default='5432'),
            }
        }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": config('DB_NAME', default='voicetrack_db'),
            "USER": config('DB_USER', default='postgres'),
            "PASSWORD": config('DB_PASSWORD', default=''),
            "HOST": config('DB_HOST', default='localhost'),
            "PORT": config('DB_PORT', default='5432'),
        }
    }

# Password validation
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
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# For App Engine, also set this
STATICFILES_DIRS = []

# Media files configuration
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# CORS Settings
CORS_ALLOW_ALL_ORIGINS = config('CORS_ALLOW_ALL_ORIGINS', default=False, cast=bool)
if not CORS_ALLOW_ALL_ORIGINS:
    CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='http://localhost:19006,http://localhost:8081').split(',')
CORS_ALLOW_CREDENTIALS = True

# API Documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'VoiceTrack API',
    'DESCRIPTION': 'API for VoiceTrack Research App - Audio recording and analysis',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# GCP Cloud Storage Settings
USE_GCP_STORAGE = config('USE_GCP_STORAGE', default=False, cast=bool)

if USE_GCP_STORAGE:
    # GCP Storage settings
    GS_BUCKET_NAME = config('GCP_STORAGE_BUCKET_NAME')
    GS_PROJECT_ID = config('GCP_PROJECT_ID')
    GS_DEFAULT_ACL = 'private'
    GS_FILE_OVERWRITE = False
    GS_LOCATION = 'media'
    
    # Use GCP Storage for media files
    DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
    
    # Static files still local for now
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
