
import os
from pathlib import Path

import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'HHggfgxfch754cnbgv')

DEBUG = os.getenv('DEBUG', True)

ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'versatileimagefield',
    'django_extensions',
    'django_filters',
    'drf_spectacular',
    'warehouse'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny"
    ],
    'EXCEPTION_HANDLER': 'core.exception_handler.custom_exception_handler',
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        'rest_framework.authentication.BasicAuthentication',
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PARSER_CLASSES": [
            'djangorestframework_camel_case.parser.CamelCaseFormParser',
            'djangorestframework_camel_case.parser.CamelCaseMultiPartParser',
            'djangorestframework_camel_case.parser.CamelCaseJSONParser',
            "rest_framework.parsers.JSONParser",
            "rest_framework.parsers.FormParser",
            "rest_framework.parsers.MultiPartParser",
        ],
    'DEFAULT_RENDERER_CLASSES': [
            'djangorestframework_camel_case.render.CamelCaseJSONRenderer',
            'djangorestframework_camel_case.render.CamelCaseBrowsableAPIRenderer',
            'rest_framework.renderers.JSONRenderer',
            'rest_framework.renderers.BrowsableAPIRenderer',
        ]
}

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'core.wsgi.application'

ALLOWED_HOSTS = ['*']


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.getenv('POSTGRES_DB', 'allflights2'),
#         'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
#         'PORT': os.getenv('POSTGRES_PORT', 5432),
#         'USER': os.getenv('POSTGRES_USER', 'victor'),
#         'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'victor'),
#     }
# }

DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://victor:victor@localhost:5432/warehouse',
        conn_max_age=600
    )
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = []
AUTH_USER_MODEL = 'warehouse.User'


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATIC_ROOT = BASE_DIR/'static'
if not DEBUG:
    STATIC_ROOT = BASE_DIR/'staticfiles'
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

STATICFILES_DIRS = []

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

MEDIA_URL = '/uploads/'

MEDIA_ROOT = BASE_DIR/'uploads'

DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

VERSATILEIMAGEFIELD_SETTINGS = {
    # cache day in seconds
    'cache_length': 2592000,
    'cache_name': 'versatileimagefield_cache',
    'jpeg_resize_quality': 70,
    'sized_directory_name': '__sized__',
    'filtered_directory_name': '__filtered__',
    'placeholder_directory_name': '__placeholder__',
    'create_images_on_demand': True,
    'image_key_post_processor': None,
    'progressive_jpeg': False,
}

VERSATILEIMAGEFIELD_RENDITION_KEY_SETS = {
    'all_image_size': [
        ('full_size', 'url'),
        ('thumbnail', 'thumbnail__100x100'),
        ('medium_square_crop', 'thumbnail__400x400'),
        ('small_square_crop', 'thumbnail__50x50'),
    ]
}

CORS_ALLOW_ALL_ORIGINS = True

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
# EMAIL_PORT = 465
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")


SPECTACULAR_SETTINGS = {
    'TITLE': 'WarehouseAPI',
    'DESCRIPTION': 'Django API for Warehouse Application',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'CAMELIZE_NAMES': True,
    # 'SCHEMA_PATH_PREFIX': '/api/v1/',
    'AUTHENTICATION_WHITELIST': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication'
    ],
    'POSTPROCESSING_HOOKS': [
            'drf_spectacular.hooks.postprocess_schema_enums',
            'drf_spectacular.contrib.djangorestframework_camel_case.camelize_serializer_fields'
        ],
    'COMPONENT_SPLIT_REQUEST': True,
}
