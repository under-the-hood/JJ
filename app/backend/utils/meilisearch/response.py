from app.backend.models.response import Response
from app.backend.utils.meilisearch.client import meili


def sync_response(response: Response):
    document = {
        "id": response.id,
        "applicant_id": response.applicant_id,
        "vacancy_id": response.vacancy_id,
        "resume_id": response.resume_id,
        "status": response.status.value,
        "resume": {
            "title": response.resume.title,
            "stack": response.resume.stack
        }
    }

    task = meili.index("responses").add_documents([document])
    finished = meili.wait_for_task(task.task_uid)
    return finished

def delete_response(response_id: int):
    meili.index("responses").delete_document(response_id)