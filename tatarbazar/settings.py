from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()  # Загружает переменные из .env
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-8!vaw*7ns$@)x3_j2a8l4a%0uh7qdyjs!84!^t_v2vev6zv0el'

OPENAI_API_KEY = config('OPENAI_API_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'store',
    'cart',
    'payment',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
]

ROOT_URLCONF = 'tatarbazar.urls'

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
                'cart.context_processors.cart',
            ],
        },
    },
]

WSGI_APPLICATION = 'tatarbazar.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        'OPTIONS': {
            'max_similarity': 0.7,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# БЕЗОПАСНОСТЬ СЕССИЙ 
SESSION_COOKIE_AGE = 7200  # 2 часа
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False  
SESSION_COOKIE_SAMESITE = 'Lax'

# CSRF защита
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = False  
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = [
    "https://*.loca.lt",
    "https://*.railway.app",
]


#STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

#  интернационализация 
LANGUAGE_CODE = 'ru-ru'  
TIME_ZONE = 'Europe/Moscow'  
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Настройки EMAIL
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.yandex.ru'          # SMTP-сервер Яндекса [citation:1][citation:4]
EMAIL_PORT = 465                       
EMAIL_USE_SSL = True                    
EMAIL_USE_TLS = False                   

EMAIL_HOST_USER = 'zukhrakamal04@yandex.ru' # Ваш полный email-адрес
EMAIL_HOST_PASSWORD = 'ozgfhhqwpbtbkbbi' 

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

PAYPAL_TEST = True
PAYPAL_RECEIVER_EMAIL = 'zukhrakamal@mail.ru'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'