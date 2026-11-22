import os
import json

if os.environ.get("DJANGO_SECRET_NAME"):
    import boto3
    secret = boto3.client("secretsmanager").get_secret_value(SecretId=os.environ["DJANGO_SECRET_NAME"])
    values = json.loads(secret["SecretString"])
    for name in ("DATABASE_URL", "DJANGO_SECRET_KEY"):
        os.environ[name] = values[name]
    del values, secret

from .common import *
from django.core.exceptions import ImproperlyConfigured

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
DEBUG = False
DATABASES = {"default": env.db("DATABASE_URL")}
db = DATABASES["default"]
if db["ENGINE"] != "django.db.backends.postgresql":
    raise ImproperlyConfigured("DATABASE_URL must use PostgreSQL")
options = db.setdefault("OPTIONS", {})
if options.setdefault("sslmode", "require") not in ("require", "verify-ca", "verify-full"):
    raise ImproperlyConfigured("DATABASE_URL requires TLS")
db.update(CONN_MAX_AGE=0, DISABLE_SERVER_SIDE_CURSORS=True)

# WhiteNoise goes right after SecurityMiddleware (first in common.MIDDLEWARE).
MIDDLEWARE = [
    MIDDLEWARE[0],
    "whitenoise.middleware.WhiteNoiseMiddleware",
    *MIDDLEWARE[1:],
    "users.cognito.RequireCognitoSession",
]
COGNITO_POOL_ID = os.environ["COGNITO_POOL_ID"]
COGNITO_DOMAIN = os.environ["COGNITO_DOMAIN"]
COGNITO_CLIENT_ID = os.environ["COGNITO_CLIENT_ID"]
AUTHENTICATION_BACKENDS = ["users.cognito.SessionBackend"]
REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework.authentication.SessionAuthentication"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
}
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
ROOT_URLCONF = "backend.aws_urls"

# --- S3 media storage ---

AWS_STORAGE_BUCKET_NAME = os.environ["AWS_STORAGE_BUCKET_NAME"]
AWS_S3_REGION_NAME = os.environ.get("AWS_REGION", "ap-northeast-1")
AWS_DEFAULT_ACL = None
AWS_S3_FILE_OVERWRITE = False

MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/"

# --- Static files ---

# CloudFront sends /static/* to the frontend bucket and /admin/* to this app,
# so the admin assets are served from the installed packages below /admin/.
STATIC_ROOT = None
STATIC_URL = "/admin/static/"
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = False
STORAGES = {
    "default": {"BACKEND": "storages.backends.s3.S3Storage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

# --- Security ---

APP_BASE = os.environ["APP_BASE"]
HTTP_PROTOCOL = "https"

ALLOWED_HOSTS = [APP_BASE, ".amazonaws.com", "localhost"] if APP_BASE else [".amazonaws.com", "localhost"]

CSRF_TRUSTED_ORIGINS = [f"https://{APP_BASE}"]
del CORS_REPLACE_HTTPS_REFERER
CORS_ALLOWED_ORIGINS = [f"https://{APP_BASE}"]
CORS_ALLOW_ALL_ORIGINS = False

# --- Logging ---

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": os.environ.get("LOG_LEVEL", "WARNING")},
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.environ.get("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        }
    },
}
