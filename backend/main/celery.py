import os

from celery import Celery
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

app = Celery('main')
app.autodiscover_tasks()
app.conf.broker_url = settings.CELERY_BROKER_URL
app.config_from_object('django.conf:settings')
