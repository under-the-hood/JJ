from celery import Celery

from backend.config import settings
from backend.models.mails import Mails
from backend.models.response import Response
from backend.models.resume import Resume
from backend.models.user import User
from backend.models.vacancy import Vacancy

celery = Celery(
    "jj_project",
    broker=settings.RABBITMQ,
    backend="redis://localhost:6379/0",
    include=["backend.utils.celery_tasks"]
)

celery.conf.task_always_eager = True