from app.backend.models.user import User
from app.backend.utils.meilisearch.client import meili


def sync_user(user: User):
    document = {
        "id": user.id,
        "email": user.email,
        "role": user.role.value,
        "name": user.name
        }

    task = meili.index("users").add_documents([document])
    finished = meili.wait_for_task(task.task_uid)
    return finished

def delete_user(user_id: int):
    meili.index("users").delete_document(user_id)