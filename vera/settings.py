import os
from django.urls import reverse_lazy

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'btcha4=9_!7*hhjka8b^m2cjih06y0amiin-ftcaweq$myl(g8_'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [os.getenv('ALLOWED_HOSTS', '*')]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'jobboard',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
    'candidateprofile',
    'vacancy',
    'quiz',
    'interview',
    'statistic',
    'material',
    'material.frontend',
    'django_filters',
    'pipeline',
    'company',
    'google_address',
    'rest_framework',
]

SITE_ID = 1

AUTH_USER_MODEL = 'users.CustomUser'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'jobboard.v_middleware.NodeMiddleware',
    'jobboard.v_middleware.RoleMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'vera.urls'

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
                'jobboard.context_processors.roles',
                'jobboard.context_processors.hints',
            ],
        },
    },
]

WSGI_APPLICATION = 'vera.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'vera_db',
        'USER': 'vera_admin' if 'DB_PASS' in os.environ.keys() else 'root',
        'PASSWORD': os.getenv('DB_PASS', '123'),
        'default-character-set': 'utf-8',
        'HOST': os.getenv('DB_HOST', 'localhost'),
    },
    'statistic': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'vera_stat',
        'USER': 'vera_admin' if 'DB_PASS' in os.environ.keys() else 'root',
        'PASSWORD': os.getenv('DB_PASS', '123'),
        'default-character-set': 'utf-8',
        'HOST': os.getenv('DB_HOST', 'localhost'),
    },
}

DATABASE_ROUTERS = ['jobboard.database_router.DBRouter', 'jobboard.database_router.PrimaryRouter']

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = '/static/'

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', '')

THEME_CONTACT_EMAIL = os.getenv('THEME_CONTACT_EMAIL', '')

VERA_COIN_CONTRACT_ADDRESS = os.getenv('VERA_COIN_CONTRACT_ADDRESS', '')

VERA_COIN_PRESALE_CONTRACT_ADDRESS = os.getenv('VERA_COIN_PRESALE_CONTRACT_ADDRESS', '')

VERA_ORACLE_CONTRACT_ADDRESS = os.getenv('VERA_ORACLE_CONTRACT_ADDRESS', '')

WEB_ETH_COINBASE = os.getenv('WEB_ETH_COINBASE', '')

COINBASE_PASSWORD_SECRET = os.getenv('COINBASE_PASSWORD', '')

ABI_PATH = 'jobboard/handlers/abi/'

NODE_URL = 'http://' + os.getenv('NODE_URL', 'localhost') + ':8545'

NET_URL = os.getenv('NET_URL', '')

LOGIN_URL = '/accounts/login'

W2V_API_URL = os.getenv('W2V_API_URL', '')

SESSION_SAVE_EVERY_REQUEST = True

# Account allauth settings
ACCOUNT_OPEN_SIGNUP = True

ACCOUNT_AUTHENTICATION_METHOD = "username_email"

ACCOUNT_EMAIL_REQUIRED = True

ACCOUNT_EMAIL_VERIFICATION = "mandatory"

ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = True

ACCOUNT_FORMS = {'signup': 'users.forms.CustomSignupForm'}

SOCIALACCOUNT_FORMS = {'signup': 'users.forms.CustomSocialSignupForm'}

ACCOUNT_ADAPTER = 'users.adapter.CustomAccountAdapter'

ACCOUNT_SESSION_REMEMBER = False

SOCIALACCOUNT_AUTO_SIGNUP = False

LOGIN_REDIRECT_URL = reverse_lazy('profile')

# Hints settings
HINTS_ENABLED = os.getenv('HINTS_ENABLED', True)

# Google address settings
GOOGLE_ADDRESS = {
    'API_KEY': os.getenv('GOOGLE_ADDRESS_API_KEY', ''),
    'API_LANGUAGE': 'en_US'
}

GOOGLE_JS_MAP_KEY = os.getenv('GOOGLE_JS_MAP_KEY', '')

# Social icons
# icon name on fontawesome, exm: 'www.<ok>.ru' -> <i class="fa fa-<odnoklassniki-square>"></i>
SOCIAL_ICONS = {
    'ok': 'odnoklassniki-square',
    'facebook': 'facebook-official',
    't': 'telegram',
    'steamcommunity': 'steam-square',
}

#  Twilio

AUTH_TOKEN = os.getenv('AUTH_TOKEN', '')

ACCOUNT_SID = os.getenv('ACCOUNT_SID', '')

AUTHY_API_KEY = os.getenv('AUTHY_API_KEY', '')

# Zoom.us account

ZOOMUS_API_KEY = os.getenv('ZOOMUS_API_KEY', '')

ZOOMUS_API_SECRET = os.getenv('ZOOMUS_API_SECRET', '')

ZOOMUS_USER_ID = os.getenv('ZOOMUS_USER_ID', '')

# email
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_PORT = 587
EMAIL_USE_TLS = True

if DEBUG:
    try:
        from vera.local_settings import *
    except Exception:
        pass
