import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "askme_nikitina.settings")

app = Celery("askme_nikitina")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()