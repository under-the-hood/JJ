import meilisearch

from app.backend.config import settings
from app.backend.models.vacancy import Vacancy
from app.backend.models.resume import Resume


meili = meilisearch.Client("http://localhost:7700", settings.MEILI_MASTER_KEY)

def init_meilisearch():
    create_vacancies_task = meili.create_index("vacancies", {"primaryKey": "id"})
    meili.wait_for_task(create_vacancies_task.task_uid)
    
    create_resumes_task = meili.create_index("resumes", {"primaryKey": "id"})
    meili.wait_for_task(create_resumes_task.task_uid)

    vacancies_index = meili.index("vacancies")
    resumes_index = meili.index("resumes")

    vacancies_index.update_searchable_attributes(["title", "city"])
    vacancies_index.update_filterable_attributes(["compensation"])

    resumes_index.update_searchable_attributes(["title", "city", "stack"])


def sync_vacancy(vacancy: Vacancy):
    document = {
        "id": vacancy.id,
        "tenant_id": vacancy.tenant_id,
        "title": vacancy.title,
        "city": vacancy.city,
        "compensation": vacancy.compensation
    }
    
    task = meili.index("vacancies").add_documents([document])
    finished = meili.wait_for_task(task.task_uid)
    return finished

def delete_vacancy(vacancy_id: int):
    meili.index("vacancies").delete_document(vacancy_id)


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