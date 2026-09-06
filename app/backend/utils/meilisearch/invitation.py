from app.backend.models.invitations import Invitation
from app.backend.utils.meilisearch.client import meili


def sync_invitation(invitation: Invitation):
    document = {
        "id": invitation.id,
        "applicant_id": invitation.applicant_id,
        "tenant_id": invitation.tenant_id,
        "resume_title": invitation.resume.title,
        "resume_stack": invitation.resume.stack,
        "vacancy_title": invitation.vacancy.title
    }
    task = meili.index("invitations").add_documents([document])
    finished = meili.wait_for_task(task.task_uid)
    return finished

def delete_invitation(invitation_id: int):
    meili.index("invitations").delete_document(invitation_id)