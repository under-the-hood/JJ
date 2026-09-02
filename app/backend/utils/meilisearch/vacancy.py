from app.backend.models.vacancy import Vacancy
from app.backend.utils.meilisearch.client import meili


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