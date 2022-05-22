import os
from .common import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')

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

ALLOWED_HOSTS = ['*']

INTERNAL_IPS = ['192.168.56.1']

INSTALLED_APPS += (
    'autofixture',
)

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, os.pardir, 'frontend', 'dist'),
]

STATIC_ROOT = os.path.join(BASE_DIR, "static")

API_BASE = "www.emonotate.com"
APPLICATION_BASE = "app.emonotate.com"
APPLICATION_URL = f"https://{APPLICATION_BASE}/"
CSRF_TRUSTED_ORIGINS = [ 
    f"https://{APPLICATION_BASE}",
    f"https://{API_BASE}"
]

CORS_ORIGIN_ALLOW_ALL = True
CSRF_COOKIE_DOMAIN = "emonotate.com"
