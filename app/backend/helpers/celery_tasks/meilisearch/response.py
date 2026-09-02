from app.backend.helpers.celery import celery
from app.backend.models.response import Response
from app.backend.database.database import celery_session
from app.backend.utils.meilisearch.response import sync_response, delete_response


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