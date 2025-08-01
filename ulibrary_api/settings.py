"""
ulibrary_api/settings.py

This file is part of the University Library project.
It contains the Django settings for the ulibrary_api project.

Generated by 'django-admin startproject' using Django 4.1.7.

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/

Author: Raul Berrios
"""
import os
from pathlib import Path
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret! Loaded from environment.
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production! Loaded from environment.
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')

# A list of strings representing the host/domain names that this Django site can serve.
ALLOWED_HOSTS = [host.strip() for host in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,api,cfmapp.com,localhost:3000,127.0.0.1:3000').split(',')]


# Application definition

# A list of all Django applications that are activated in this Django instance.
INSTALLED_APPS = [
    # 3rd Party Apps
    'grappelli',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',  # WhiteNoise for static file serving
    'corsheaders',  # CORS headers for cross-origin requests
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework.authtoken',
    'drf_spectacular',
    'django_extensions',

    # Local Apps
    'library',
]

# A list of middleware to be executed for each request/response.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # Should be placed high, but after SecurityMiddleware.
    'whitenoise.middleware.WhiteNoiseMiddleware',  # WhiteNoise middleware for static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# The root URL configuration for the project.
ROOT_URLCONF = 'ulibrary_api.urls'

# Configuration for the template engines.
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

# The entry-point for WSGI-compatible web servers to serve the project.
WSGI_APPLICATION = 'ulibrary_api.wsgi.application' 


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

# Database configuration. Uses dj_database_url to parse the DATABASE_URL environment variable.
DATABASES = {}
if 'DATABASE_URL' in os.environ:
    DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=False)


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators
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
# https://docs.djangoproject.com/en/4.1/ref/settings/#i18n

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'

# The absolute path to the directory where collectstatic will collect static files for deployment.
# This is necessary for serving admin static files in production.
STATIC_ROOT = BASE_DIR / "staticfiles"

# Use Whitenoise's storage backend for compressed static files and caching.
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'library.User'

# Django REST Framework global settings.
REST_FRAMEWORK = {
    # Default authentication schemes. TokenAuthentication is used for API clients.
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',  # Not needed for API-only apps
    ],
    # Default permission policy. Requires users to be authenticated for all endpoints.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    # The default schema generator for API documentation.
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
     # Default pagination settings for API views.
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
}

# CORS Settings - a list of origins that are authorized to make cross-site HTTP requests.
# Update this to your React app's URL in production.
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in os.getenv('CORS_ALLOWED_ORIGINS', "http://localhost:3000,http://127.0.0.1:3000,http://localhost,http://cfmapp.com").split(',')]
CORS_ALLOW_CREDENTIALS = True  # Allow cookies to be included in cross-origin requests

# CSRF Trusted Origins - a list of hosts that are trusted for cross-site requests.
# This is necessary for POST requests (like admin login) to work from your domain.
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in os.getenv('CSRF_TRUSTED_ORIGINS', 'http://localhost,http://127.0.0.1,http://cfmapp.com,http://localhost:3000,http://127.0.0.1:3000').split(',')]


# drf-spectacular settings for generating OpenAPI schema and Swagger UI.
SPECTACULAR_SETTINGS = {
    'TITLE': 'University Library API',
    'DESCRIPTION': 'API for the University Library System.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_SETTINGS': {
        'persistAuthorization': True,  # Keep the user authorized on page refresh
    },
    'COMPONENTS': {
        'securitySchemes': {
            'tokenAuth': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization',
                'description': 'Token-based authentication. Use the format: **`Token <your_token_here>`**'
            }
        }
    }
}

# Grappelli Settings
GRAPPELLI_ADMIN_TITLE = "ULibrary Administration"
