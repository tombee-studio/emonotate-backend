import os
from .common import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USERNAME'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('DATABASE_HOST'),
        'PORT': os.getenv('DATABASE_PORT'),
    }
}

INTERNAL_IPS = ['192.168.56.1']

INSTALLED_APPS += (
    'autofixture',
)

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, os.pardir, 'frontend', 'dist'),
    os.path.join(BASE_DIR, "static"),
]

EMAIL_BACKEND = os.environ['EMAIL_BACKEND']
EMAIL_HOST = os.environ['EMAIL_HOST']
EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
EMAIL_PORT = os.environ['EMAIL_PORT']

API_BASE = "enigmatic-thicket-08912.herokuapp.com"
APPLICATION_BASE = "vast-scrubland-26728.herokuapp.com"
APPLICATION_URL = f"https://{APPLICATION_BASE}/"
CSRF_TRUSTED_ORIGINS = [ 
    f"https://{APPLICATION_BASE}", 
    f"https://{API_BASE}" 
]

CORS_ORIGIN_WHITELIST += f"https://{APPLICATION_BASE}"
CORS_ORIGIN_WHITELIST += f"https://{API_BASE}"

CORS_ORIGIN_ALLOW_ALL = True
CSRF_COOKIE_DOMAIN = "herokuapp.com"
