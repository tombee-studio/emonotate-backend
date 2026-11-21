"""Local settings for the Cognito and media integration tests."""
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / 'apps'))

SECRET_KEY = 'local-test-emonotate-secret'
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
AUTH_USER_MODEL = 'users.EmailUser'
INSTALLED_APPS = ['django.contrib.auth', 'django.contrib.contenttypes', 'django.contrib.sessions', 'rest_framework', 'users']
MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'users.cognito.RequireCognitoSession',
]
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
