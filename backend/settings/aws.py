import json
import os
import boto3
from botocore.exceptions import ClientError
from .common import *

# --- Secrets Manager helper ---

def _get_secret(secret_name: str) -> dict:
    client = boto3.client("secretsmanager", region_name=os.environ.get("AWS_REGION", "ap-northeast-1"))
    try:
        response = client.get_secret_value(SecretId=secret_name)
    except ClientError as exc:
        raise RuntimeError(f"Failed to retrieve secret '{secret_name}': {exc}") from exc
    return json.loads(response["SecretString"])


_secret = _get_secret(os.environ["DJANGO_SECRET_NAME"])

SECRET_KEY = _secret["DJANGO_SECRET_KEY"]
DEBUG = os.environ.get("DEBUG", "False") == "True"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": _secret.get("DB_NAME", "emonotate"),
        "USER": _secret["DB_USER"],
        "PASSWORD": _secret["DB_PASSWORD"],
        "HOST": _secret["DB_HOST"],
        "PORT": _secret.get("DB_PORT", "5432"),
    }
}

# --- S3 media storage ---

AWS_STORAGE_BUCKET_NAME = os.environ["AWS_STORAGE_BUCKET_NAME"]
AWS_S3_REGION_NAME = os.environ.get("AWS_REGION", "ap-northeast-1")
AWS_S3_CUSTOM_DOMAIN = None
AWS_DEFAULT_ACL = None
AWS_S3_FILE_OVERWRITE = False

DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/"

# --- Static files ---

STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "/static/"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# --- Security ---

API_BASE = os.environ.get("API_BASE", "")
APPLICATION_BASE = os.environ.get("APP_BASE", "")
HTTP_PROTOCOL = "https"
APPLICATION_URL = f"{HTTP_PROTOCOL}://{APPLICATION_BASE}/"

ALLOWED_HOSTS = [API_BASE, APPLICATION_BASE, ".amazonaws.com", "localhost"]

CSRF_TRUSTED_ORIGINS = [
    f"{HTTP_PROTOCOL}://{APPLICATION_BASE}",
    f"{HTTP_PROTOCOL}://{API_BASE}",
]

CORS_ORIGIN_WHITELIST = [
    f"{HTTP_PROTOCOL}://{APPLICATION_BASE}",
    f"{HTTP_PROTOCOL}://{API_BASE}",
]

CORS_ORIGIN_ALLOW_ALL = False

# --- Logging ---

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": os.environ.get("LOG_LEVEL", "WARNING"),
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.environ.get("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
    },
}
