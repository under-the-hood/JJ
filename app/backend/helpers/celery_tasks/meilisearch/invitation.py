from app.backend.helpers.celery import celery
from app.backend.models.invitations import Invitation
from app.backend.utils.meilisearch.invitation import sync_invitation, delete_invitation
from app.backend.database.database import celery_session


@celery.task(name="sync_invitation_task")
def sync_invitation_task(invitation_id: int):
    with celery_session() as session:
        resume = session.query(Invitation).filter(Invitation.id == invitation_id).first()
        if not resume:
            return "Resume not found"
            
        return sync_invitation(resume).status

@celery.task(name="delete_invitation_task")
def delete_invitation_task(invitation_id: int):
    delete_invitation(invitation_id)
    return "deleted"