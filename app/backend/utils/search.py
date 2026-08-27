import meilisearch

from app.backend.config import settings
from app.backend.models.vacancy import Vacancy
from app.backend.models.resume import Resume
from app.backend.models.user import User
from app.backend.models.response import Response


meili = meilisearch.Client(f"http://{settings.MEILI_HTTP_ADDR}:7700", settings.MEILI_MASTER_KEY)

def init_meilisearch():
    create_vacancies_task = meili.create_index("vacancies", {"primaryKey": "id"})
    meili.wait_for_task(create_vacancies_task.task_uid)
    
    create_resumes_task = meili.create_index("resumes", {"primaryKey": "id"})
    meili.wait_for_task(create_resumes_task.task_uid)

    create_users_task = meili.create_index("users", {"primaryKey": "id"})
    meili.wait_for_task(create_users_task.task_uid)

    create_responses_task = meili.create_index("responses", {"primaryKey": "id"})
    meili.wait_for_task(create_responses_task.task_uid)

    vacancies_index = meili.index("vacancies")
    resumes_index = meili.index("resumes")
    users_index = meili.index("users")
    responses_index = meili.index("responses")

    vacancies_index.update_searchable_attributes(["title", "city"])
    vacancies_index.update_filterable_attributes(["compensation"])

    resumes_index.update_searchable_attributes(["title", "city", "stack"])

    users_index.update_searchable_attributes(["email", "name"])

    responses_index.update_searchable_attributes(["resume.title", "resume.stack"])
    responses_index.update_filterable_attributes(["status"])


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