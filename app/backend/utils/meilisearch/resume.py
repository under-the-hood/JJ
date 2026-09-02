from app.backend.models.resume import Resume
from app.backend.utils.meilisearch.client import meili


def sync_resume(resume: Resume):
    document = {
        "id": resume.id,
        "applicant_id": resume.applicant_id,
        "title": resume.title,
        "about": resume.about,
        "stack": resume.stack,
        "city": resume.city

    }
    task = meili.index("resumes").add_documents([document])
    finished = meili.wait_for_task(task.task_uid)
    return finished

def delete_resume(resume_id: int):
    meili.index("resumes").delete_document(resume_id)