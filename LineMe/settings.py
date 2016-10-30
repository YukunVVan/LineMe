"""
Django settings for LineMe project.

Generated by 'django-admin startproject' using Django 1.8.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import logging
import os
import platform

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '0jh#joni6e@5j!s%6a0%05xs%%^$x3@=l7fs5&ndfrchq5-tn-'

# SECURITY WARNING: don't run with debug turned on in production!
if platform.system() == 'Linux':
    DEPLOYMENT = True
else:
    DEPLOYMENT = False
DEBUG = not DEPLOYMENT

ALLOWED_HOSTS = ['lime.seeleit.com']

# SSL
if DEPLOYMENT:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    # SECURE_SSL_REDIRECT = True

DEPLOYED_LANGUAGE = 'zh-cn'


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'compressor',
    'iauth',
    'friendnet',
)

MIDDLEWARE_CLASSES = (
    # 'django.middleware.cache.UpdateCacheMiddleware',
    'htmlmin.middleware.HtmlMinifyMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    # 'django.middleware.cache.FetchFromCacheMiddleware',
    'htmlmin.middleware.MarkRequestMiddleware',
)

ROOT_URLCONF = 'LineMe.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'LineMe.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

if not DEPLOYMENT:
    # DATABASES = {
    #     'default': {
    #         'ENGINE': 'django.db.backends.mysql',
    #         'NAME': 'lineme',
    #         'USER': 'root',
    #         'PASSWORD': '12345678',
    #         'HOST': '127.0.0.1',
    #         'PORT': '3306',
    #     }
    # }

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'lineme',
            'USER': 'postgres',
            'PASSWORD': '12345678',
            'HOST': '127.0.0.1',
            'PORT': '5432',
        }
    }

    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }

else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'lineme',
            'USER': 'postgres',
            'PASSWORD': '12345678',
            'HOST': '127.0.0.1',
            'PORT': '5432',
        }
    }

    # CACHES = {
    #     'default': {
    #         'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
    #         'LOCATION': '127.0.0.1:11211',
    #         'TIMEOUT': 60 * 15,
    #         # 'OPTIONS': {
    #         #     'server_max_value_length': 1024 * 1024 * 128,
    #         # }
    #     }
    # }

    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://127.0.0.1:6379/1",
            'TIMEOUT': 60 * 10,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        }
    }

    # CACHES = {
    #     'default': {
    #         'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    #         'LOCATION': 'unique-snowflake',
    #     }
    # }


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'static'),
#     os.path.join(BASE_DIR, 'media'),
# ]

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # other finders..
    'compressor.finders.CompressorFinder',
)

# HTML_MINIFY = True
EXCLUDE_FROM_MINIFYING = ['^search/', '^egraph/', '^ggraph/',
                          '^gmap/', '^gthree/', '^show/data/']

# COMPRESS_ENABLED = True
COMPRESS_OUTPUT_DIR = 'compressed'
COMPRESS_CSS_FILTERS = ['compressor.filters.css_default.CssAbsoluteFilter',
                        'compressor.filters.cssmin.CSSCompressorFilter']

LOGIN_URL = '/login/'


# Email
if DEPLOYMENT:
    EMAIL_BACKEND = 'django_smtp_ssl.SSLEmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'smtp.126.com'
EMAIL_PORT = 465
EMAIL_HOST_USER = 'cnclineme@126.com'
EMAIL_HOST_PASSWORD = 'SJTUcnc2310'
EMAIL_USE_TLS = True


# Log
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s: %(message)s <%(module)s %(funcName)s>',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/lineme.log').replace('\\', '/'),
            'formatter': 'verbose'
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        # 'django.request': {
        #     'handlers': ['file'],
        #     'level': 'ERROR',
        #     'propagate': False,
        # },
        'lineme_logger': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

logger = logging.getLogger('lineme_logger')
