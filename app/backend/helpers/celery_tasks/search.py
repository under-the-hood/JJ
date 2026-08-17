from app.backend.helpers.celery import celery
from app.backend.models.vacancy import Vacancy
from app.backend.models.resume import Resume
from app.backend.database.database import celery_session
from app.backend.utils.search import sync_vacancy, sync_resume, delete_vacancy, delete_resume


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


@celery.task(name="sync_resumes_task")
def sync_resume_task(resume_id: int):
    with celery_session() as session:
        resume = session.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            return "Resume not found"
            
        return sync_resume(resume).status

@celery.task(name="delete_resume_task")
def delete_resume_task(resume_id: int):
    delete_resume(resume_id)
    return "deleted"