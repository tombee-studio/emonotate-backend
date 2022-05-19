"""
WSGI config for backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os
from dotenv import load_dotenv
load_dotenv()

try:
    basestring
except NameError:
    basestring = str

from django.core.wsgi import get_wsgi_application

STAGE = os.environ["STAGE"]
os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"backend.settings.{STAGE.lower()}")

application = get_wsgi_application()
