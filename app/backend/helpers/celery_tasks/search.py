from app.backend.helpers.celery import celery
from app.backend.models.vacancy import Vacancy
from app.backend.models.resume import Resume
from app.backend.models.response import Response
from app.backend.database.database import celery_session
from app.backend.utils.search import sync_vacancy, sync_resume, sync_user, sync_response, delete_vacancy, delete_resume, delete_user, delete_response
from app.backend.models.user import User


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


@celery.task(name="sync_resume_task")
def sync_resume_task(resume_id: int):
    with celery_session() as session:
        resume = session.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            return "Resume not found"
            
        return sync_resume(resume).status

@celery.task(name="delete_resumes_task")
def delete_resume_task(resume_id: int):
    delete_resume(resume_id)
    return "deleted"


@celery.task(name="sync_user_task")
def sync_user_task(user_id: int):
    with celery_session() as session:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return "User not found"

        return sync_user(user).status

@celery.task(name="delete_user_task")
def delete_user_task(user_id: int):
    delete_user(user_id)
    return "deleted"


@celery.task(name="sync_response_task")
def sync_response_task(response_id: int):
    with celery_session() as session:
        response = session.query(Response).filter(Response.id == response_id).first()
        if not response:
            return "Response not found"

        return sync_response(response).status

@celery.task(name="delete_response_task")
def delete_response_task(response_id: int):
    delete_response(response_id)
    return "deleted"