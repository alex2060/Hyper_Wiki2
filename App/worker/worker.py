import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'App.settings')
app = Celery()
app.conf.update(settings.CELERY)
