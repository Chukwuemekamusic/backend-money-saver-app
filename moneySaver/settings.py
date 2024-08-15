from pathlib import Path
from datetime import timedelta
import os
# from environ import Env 
from dotenv import load_dotenv
import dj_database_url
# from dotenv import load_dotenv

# load_dotenv()

load_dotenv()
# env = Env()
# Env.read_env()

GOOGLE_OAUTH2_PROJECT_ID = os.getenv('GOOGLE_OAUTH2_PROJECT_ID', default='')
GOOGLE_OAUTH2_CLIENT_ID = os.getenv('GOOGLE_OAUTH2_CLIENT_ID', default='')
GOOGLE_OAUTH2_CLIENT_SECRET = os.getenv('GOOGLE_OAUTH2_CLIENT_SECRET', default='')
BASE_FRONTEND_URL = os.getenv('BASE_FRONTEND_URL', default='')
BASE_APP_URL = os.getenv('BASE_APP_URL', default='')
BASE_API_URL = os.getenv('BASE_API_URL', default='')

# print(f"GOOGLE_OAUTH2_CLIENT_ID: {GOOGLE_OAUTH2_CLIENT_ID}")
# print(f"GOOGLE_OAUTH2_CLIENT_SECRET: {GOOGLE_OAUTH2_CLIENT_SECRET}")

ENVIRONMENT = os.getenv('ENVIRONMENT', default='production')
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
if ENVIRONMENT == ('development'):
    DEBUG = True
else:
    DEBUG = False

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # for allauth
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # 'allauth.socialaccount.providers.google',
    "dj_rest_auth",
    "dj_rest_auth.registration",
    "rest_framework.authtoken",
    
    # end for allauth

    'api',

    'rest_framework',
    'django_extensions',
    "corsheaders",
    'knox',

    'drf_yasg',
    
    

]

AUTH_USER_MODEL = 'api.CustomUser'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    "whitenoise.middleware.WhiteNoiseMiddleware",

    # corsheader
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    # end corsheader

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # #TODO: Add the account middleware:
    # "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = 'moneySaver.urls'

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

WSGI_APPLICATION = 'moneySaver.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'money_saver_app',
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('MY_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',
    }
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': BASE_DIR / 'db.sqlite3',
    # }
}

POSTGRES_LOCALLY = False
if ENVIRONMENT == 'production' or not POSTGRES_LOCALLY: 
    DATABASES['default'] = dj_database_url.parse(os.getenv('DATABASE_URL'))


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIR = [ BASE_DIR/ 'static' ]
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ('knox.auth.TokenAuthentication',),
}

REST_KNOX = {
    'SECURE_HASH_ALGORITHM': 'cryptography.hazmat.primitives.hashes.SHA512',
    'AUTH_TOKEN_CHARACTER_LENGTH': 64,
    'TOKEN_TTL': timedelta(hours=24),
    'USER_SERIALIZER': 'knox.serializers.UserSerializer',
    'TOKEN_LIMIT_PER_USER': None,
    'AUTO_REFRESH': False,
    # 'EXPIRY_DATETIME_FORMAT': api_settings.DATETME_FORMAT,
}

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

SITE_ID = 1

# if ENVIRONMENT == 'production' or POSTGRES_LOCALLY == False:
#     EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# else:
#     EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = "smtp.gmail.com"                   
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')              # your email address
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD') 
EMAIL_USE_TLS = False                               # False
EMAIL_PORT = "587"    
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
DEFAULT_FROM_EMAIL = f"Moneysaver <{os.getenv('EMAIL_HOST_USER')}>"
ACCOUNT_EMAIL_SUBJECT_PREFIX = ''

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"

# <EMAIL_CONFIRM_REDIRECT_BASE_URL>/<key>
# <PASSWORD_RESET_CONFIRM_REDIRECT_BASE_URL>/<uidb64>/<token>/
if ENVIRONMENT == 'development' or POSTGRES_LOCALLY is True:
    EMAIL_CONFIRM_REDIRECT_BASE_URL = \
    "http://localhost:3000/verify-email/"
    
    PASSWORD_RESET_CONFIRM_REDIRECT_BASE_URL = \
    "http://localhost:3000/password-reset/confirm/"
else:
    EMAIL_CONFIRM_REDIRECT_BASE_URL = \
    BASE_FRONTEND_URL + "/verify-email/"

    PASSWORD_RESET_CONFIRM_REDIRECT_BASE_URL = \
    BASE_FRONTEND_URL + "/password-reset/confirm/"
