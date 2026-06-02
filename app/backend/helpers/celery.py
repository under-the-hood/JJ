from celery import Celery

from app.backend.config import settings


celery = Celery(
    "jj_project",
    broker=f"{settings.RABBITMQ}",
    backend=f"redis://{settings.REDIS_HOST}:6379/0",
    include=["app.backend.helpers.celery_tasks"]
)