"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 4.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-cvrrc(n1vk&o=h#3uk9nmayv)z0*50gw%%zk!9w5tb8y*g)%ai'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

AUTHENTICATION_BACKENDS = (
                            'django.contrib.auth.backends.ModelBackend',
                            'allauth.account.auth_backends.AuthenticationBackend',
                        )

LOCALE_PATHS = (
                    os.path.join(BASE_DIR, 'templates', 'locale'),
                )

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    ## 보안 인증관련 앱
    'sslserver',

    ## 프로젝트에 사용되고 있는 앱들
    'main.apps.MainConfig',
    'UserProfile.apps.UserprofileConfig',
    'community.apps.CommunityConfig',
    'gamedb.apps.GamedbConfig',
    'news.apps.NewsConfig',

    ## 기능 테스트에서 사용하고 있는 앱
    'experiment.apps.ExperimentConfig',

    ## 소셜 로그인 관련 앱
    'allauth',
    'allauth.account',
    'django.contrib.sites',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.kakao',
    'allauth.socialaccount.providers.naver',
]

SITE_ID = 1

## 로그인 후 redirect되는 경로
LOGIN_REDIRECT_URL          = '/'

## 로그아웃 후 redirect되는 경로
ACCOUNT_LOGOUT_REDIRECT_URL = '/'

## 로그아웃 버튼 클릭 시 자동 로그아웃
ACCOUNT_LOGOUT_ON_GET       = True

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
                    os.path.join(BASE_DIR, 'templates'), 
                    os.path.join(BASE_DIR, 'templates', 'account'),
                    os.path.join(BASE_DIR, 'templates', 'openin'),
                    os.path.join(BASE_DIR, 'templates', 'socialaccount'),
                ],
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

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


## 로깅용 설정
LOGGING = {
    'version' : 1,

    ## 기존의 로거들 비활성화 (이전 버전과의 호환성 문제로 설정)
    'disable_existing_loggers' : False,
    'handlers' : {
        'console' : {
            'class' : 'logging.StreamHandler'
        },
    },

    'loggers' : {
        'my_logger' : {
            'handlers' : ['console'],
            'level' : 'INFO'
        }
    }

}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'ko-KR'
LANGUAGES = [
                ('ko', _('Korean')),
                ('en', _('English')),
            ]

TIME_ZONE = 'UTC'
USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/
STATIC_URL = '/templates/static/'
STATIC_DIR = os.path.join(BASE_DIR, 'templates/static/')

STATICFILES_DIRS = [ BASE_DIR / STATIC_DIR ]
STATIC_ROOT      = os.path.join(BASE_DIR, '.static_root')

MEDIA_URL  = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD      = 'django.db.models.BigAutoField'
