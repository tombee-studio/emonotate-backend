import os
from .common import *

# --- Core ---

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
DEBUG = os.environ.get("DEBUG", "False") == "True"

# --- Database (Aurora Serverless v1 via env vars) ---

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "emonotate"),
        "USER": os.environ.get("DB_USER", "emonotate"),
        "PASSWORD": os.environ["DB_PASSWORD"],
        "HOST": os.environ["DB_HOST"],
        "PORT": os.environ.get("DB_PORT", "5432"),
        "CONN_MAX_AGE": 0,
    }
}

# --- S3 media storage ---

AWS_STORAGE_BUCKET_NAME = os.environ["AWS_STORAGE_BUCKET_NAME"]
AWS_S3_REGION_NAME = os.environ.get("AWS_REGION", "ap-northeast-1")
AWS_DEFAULT_ACL = None
AWS_S3_FILE_OVERWRITE = False

DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/"

# --- Static files ---

STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "/static/"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# --- Security ---

APP_BASE = os.environ.get("APP_BASE", "")
HTTP_PROTOCOL = "https"

ALLOWED_HOSTS = [APP_BASE, ".amazonaws.com", "localhost"] if APP_BASE else [".amazonaws.com", "localhost"]

CSRF_TRUSTED_ORIGINS = [f"{HTTP_PROTOCOL}://{APP_BASE}"] if APP_BASE else []
CORS_ORIGIN_WHITELIST = [f"{HTTP_PROTOCOL}://{APP_BASE}"] if APP_BASE else []
CORS_ORIGIN_ALLOW_ALL = not bool(APP_BASE)

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
