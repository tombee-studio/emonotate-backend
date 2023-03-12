import os
import sys

import redis
from rq import Worker, Queue, Connection
from django.conf import settings
import django

try:
    basestring
except NameError:
    basestring = str

listen = ['high', 'default', 'low']

redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
sys.path.append(os.path.join(f"{os.getcwd()}/backend", 'apps'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"backend.settings.common")

django.setup()

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()