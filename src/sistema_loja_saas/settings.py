"""
Django settings for sistema_loja_saas project.

Generated by 'django-admin startproject' using Django 5.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os
import environ
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


env = environ.Env()
env.read_env(os.path.join(BASE_DIR, '.env'))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-9%l$p%)=axnxsnupc4pm6x2k1%_e=js$uuqwdw7)$+mg=hc7ao'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'util',
    'scope_auth',
    'common',
    'loja',
    'saas'
]

# Configura o backend da autenticação

AUTHENTICATION_BACKENDS = ['scope_auth.backends.ModelScopeBackend']

# Configura o usuário personalizado

AUTH_USER_MODEL = 'common.UsuarioGenerico'


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sistema_loja_saas.urls'

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

WSGI_APPLICATION = 'sistema_loja_saas.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DATABASE_NAME'),
        'USER': env('DATABASE_USER'),
        'PASSWORD': env('DATABASE_PASSWORD'),
        'HOST': env('DATABASE_HOST'),
        'PORT': env('DATABASE_PORT'),
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

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuração dos loggers
LOGS_DIR = os.path.join(BASE_DIR, '../logs/')

os.makedirs(f'{LOGS_DIR}', exist_ok=True)
if not os.path.exists(f'{LOGS_DIR}logs.csv'):
    csv = open(f'{LOGS_DIR}logs.csv', 'a')
    csv.write('DateTime,Level,App,Mensagem\n')
    csv.close()


LOGGING = {
    'version': 1,
    'loggers': {
        'debug': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'debug-verbose': {
            'handlers': ['console-v', 'csv'],
            'level': 'DEBUG',
        },
        'product': {
            'handlers': ['console-v', 'file', 'csv'],
            'level': 'WARNING',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'filters': ['app_label_filter'],
        },
        'console-v': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'filters': ['app_label_filter'],
        },
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_DIR, 'logs.log'),
            'formatter': 'file',
            'filters': ['app_label_filter'],
        },
        'csv': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_DIR, 'logs.csv'),
            'formatter': 'csv',
            'filters': ['app_label_filter'],
        },
    },
    'formatters': {
        'simple': {
            '()': 'util.logging.DjangoColorsFormatter',
            'format': '[{levelname}]{pathname} [{app_label}] {message}',
            'style': '{',
        },
        'verbose': {
            '()': 'util.logging.DjangoColorsFormatter',
            'format': '{levelname}:{asctime}:{pathname}{app_label}:{module}: {message}',
            'style': '{',
        },
        'file': {
            '()': 'util.logging.ExcInfoInlineFormatter',
            'format': '{levelname}:{asctime}:{pathname}{app_label}:{module}: {message}',
            'style': '{',
        },
        'csv': {
            '()': 'util.logging.CSVFormatter',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'format': '{asctime},{levelname},{pathname}{app_label},"{message}"',
            'style': '{',
        }
    },
    'filters': {
        'app_label_filter': {
            '()': 'util.logging.AppLabelFilter',
        },
    },
}
