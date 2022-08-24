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
        'HOST': "localhost",
        'PORT': os.getenv('DATABASE_PORT'),
        'TEST': {
            'NAME': os.getenv('TEST_DATABASE_NAME'),
        }
    }
}

INTERNAL_IPS = ['192.168.56.1']

INSTALLED_APPS += (
)

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, os.pardir, 'frontend', 'build'),
    os.path.join(BASE_DIR, "static"),
]

EMAIL_BACKEND = os.environ['DEBUG_EMAIL_BACKEND']

NOSE_ARGS = [
    '--nocapture',
    '--nologcapture',
]

APPLICATION_BASE = "127.0.0.1:3000"
APPLICATION_URL = f"http://{APPLICATION_BASE}/"

CORS_ORIGIN_ALLOW_ALL = True
