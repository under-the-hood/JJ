from app.backend.helpers.celery import celery
from app.backend.models.resume import Resume
from app.backend.utils.meilisearch.resume import sync_resume, delete_resume
from app.backend.database.database import celery_session


@celery.task(name="sync_resume_task")
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