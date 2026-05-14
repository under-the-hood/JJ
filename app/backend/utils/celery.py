from celery import Celery

from app.backend.config import settings
from app.backend.models.mails import Mails
from app.backend.models.response import Response
from app.backend.models.resume import Resume
from app.backend.models.user import User
from app.backend.models.vacancy import Vacancy

celery = Celery(
    "jj_project",
    broker=f"{settings.RABBITMQ}",
    backend=f"redis://{settings.REDIS_HOST}:6379/0",
    include=["backend.utils.celery_tasks"]
)