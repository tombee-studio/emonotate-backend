"""Local settings for the Cognito and media integration tests."""
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / 'apps'))

SECRET_KEY = 'local-test-emonotate-secret'
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
AUTH_USER_MODEL = 'users.EmailUser'
INSTALLED_APPS = [
    'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes', 'django.contrib.sessions',
    'django.contrib.messages', 'django.contrib.staticfiles', 'rest_framework', 'users',
]
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'users.cognito.RequireCognitoSession',
]
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]
STATIC_URL = '/admin/static/'
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = False
ROOT_URLCONF = 'backend.aws_urls'
AUTHENTICATION_BACKENDS = ['users.cognito.SessionBackend']
APP_BASE = 'testserver'
COGNITO_DOMAIN = 'https://example.auth.ap-northeast-1.amazoncognito.com'
COGNITO_CLIENT_ID = 'client'
COGNITO_POOL_ID = 'pool'
AWS_S3_REGION_NAME = 'ap-northeast-1'
AWS_STORAGE_BUCKET_NAME = 'test-emonotate'
MEDIA_URL = 'https://test-emonotate.s3.ap-northeast-1.amazonaws.com/'
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated', 'backend.permissions.DjangoModelViewPermissions',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework.authentication.SessionAuthentication'],
    'DEFAULT_PAGINATION_CLASS': 'backend.pagination.StandardPagination',
}
