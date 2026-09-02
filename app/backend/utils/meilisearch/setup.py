from app.backend.utils.meilisearch.client import meili


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
    responses_index.update_filterable_attributes(["status", "vacancy_id"])