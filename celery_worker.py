# celery_worker.py
from celery import Celery
import os
from app.core.config import settings

redis_url = settings.REDIS_URL
celery_app = Celery(
    "fastapi_celery_app",
    broker=redis_url,
    backend=redis_url,
    include=['app.tasks'] # Assuming your tasks are in app/tasks.py
)

# Optional: Configure task serialization
celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
)