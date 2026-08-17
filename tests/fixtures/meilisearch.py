import pytest

from app.backend.utils.search import meili


@pytest.fixture(autouse=True)
async def clean_meilisearch():
    for index_name in ("vacancies", "resumes"):
        task = meili.index(index_name).delete_all_documents()
        meili.wait_for_task(task.task_uid)

    yield