import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings.aws")

from mangum import Mangum
from backend.asgi import application

_mangum = Mangum(application, lifespan="off")


def handler(event, context):
    # Allow management commands via {"manage": "migrate --run-syncdb"} etc.
    if "manage" in event:
        import io
        import shlex
        from django.db import connections
        from django.core.management import call_command

        # Force-reset any stale DB connections from previous invocations
        for alias in connections:
            conn = connections[alias]
            try:
                conn.close()
            except Exception:
                pass
            conn.connection = None  # Make Django open a fresh connection

        args = shlex.split(event["manage"])
        out = io.StringIO()
        try:
            call_command(*args, stdout=out, stderr=out)
            return {"status": "ok", "output": out.getvalue()}
        except Exception as exc:
            return {"status": "error", "error": str(exc), "output": out.getvalue()}

    return _mangum(event, context)
