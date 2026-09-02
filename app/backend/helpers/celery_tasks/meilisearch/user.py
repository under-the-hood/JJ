from app.backend.helpers.celery import celery
from app.backend.database.database import celery_session
from app.backend.utils.meilisearch.user import sync_user, delete_user
from app.backend.models.user import User


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