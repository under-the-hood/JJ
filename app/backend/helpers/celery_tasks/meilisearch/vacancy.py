from app.backend.helpers.celery import celery
from app.backend.models.vacancy import Vacancy
from app.backend.database.database import celery_session
from app.backend.utils.meilisearch.vacancy import sync_vacancy, delete_vacancy


@celery.task(name="sync_vacancy_task")
def sync_vacancy_task(vacancy_id: int):
    with celery_session() as session:
        vacancy = session.query(Vacancy).filter(Vacancy.id == vacancy_id).first()
        if not vacancy:
            return "Vacancy not found"

        return sync_vacancy(vacancy).status

@celery.task(name="delete_vacancy_task")
def delete_vacancy_task(vacancy_id: int):
    delete_vacancy(vacancy_id)
    return "deleted"