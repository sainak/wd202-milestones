import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task_manager.settings.local")
app = Celery("task_manager")
app.config_from_object("django.conf:settings")
app.autodiscover_tasks()
