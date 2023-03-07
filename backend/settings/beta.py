import io
import os
from .common import *
import google.auth
from google.cloud import secretmanager

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# Attempt to load the Project ID into the environment, safely failing on error.
try:
    _, os.environ["GOOGLE_CLOUD_PROJECT"] = google.auth.default()
except google.auth.exceptions.DefaultCredentialsError:
    pass

if os.path.isfile(env_file):
    # Use a local secret file, if provided

    env.read_env(env_file)
# [START_EXCLUDE]
elif os.getenv("TRAMPOLINE_CI", None):
    # Create local settings if running with CI, for unit testing

    placeholder = (
        f"SECRET_KEY=a\n"
        "GS_BUCKET_NAME=None\n"
        f"DATABASE_URL=sqlite://{os.path.join(BASE_DIR, 'db.sqlite3')}"
    )
    env.read_env(io.StringIO(placeholder))
# [END_EXCLUDE]
elif os.environ.get("GOOGLE_CLOUD_PROJECT", None):
    # Pull secrets from Secret Manager
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")

    client = secretmanager.SecretManagerServiceClient()
    settings_name = os.environ.get("SETTINGS_NAME", "django_settings")
    name = f"projects/{project_id}/secrets/{settings_name}/versions/latest"
    payload = client.access_secret_version(name=name).payload.data.decode("UTF-8")

    env.read_env(io.StringIO(payload))
else:
    raise Exception("No local .env or GOOGLE_CLOUD_PROJECT detected. No secrets found.")


DATABASES = {
    'default': env.db()
}

if os.getenv("USE_CLOUD_SQL_AUTH_PROXY", None):
    DATABASES["default"]["HOST"] = "127.0.0.1"
    DATABASES["default"]["PORT"] = 8100

INTERNAL_IPS = ['192.168.56.1']

INSTALLED_APPS += (
)

STATICFILES_DIRS = [
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

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')

CSRF_TRUSTED_ORIGINS=['https://emonotate-backend-b7ramgi3ga-an.a.run.app']
