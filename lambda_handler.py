import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings.aws")

from mangum import Mangum
from backend.asgi import application

handler = Mangum(application, lifespan="off")
