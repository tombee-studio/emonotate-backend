import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings.aws")

from mangum import Mangum
from backend.wsgi import application

handler = Mangum(application, lifespan="off")
