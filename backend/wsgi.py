"""
WSGI config for backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os
from dotenv import load_dotenv
load_dotenv()

from django.core.wsgi import get_wsgi_application

STAGE = os.environ["STAGE"]
if STAGE == "DEVL":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings.devl")
elif STAGE == "ALPHA":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings.alpha")
elif STAGE == "PROD":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings.prod")
else:
    raise "ステージ: {}は登録されてません".format(STAGE)
    exit(-1)

application = get_wsgi_application()
