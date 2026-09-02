import pytest

from app.backend.models.vacancy import Vacancy
from app.backend.utils.meilisearch.vacancy import sync_vacancy
from app.backend.utils.meilisearch.client import meili


@pytest.mark.asyncio
async def test_meilisearch_sync(create_vacancy, test_session):
    vacancy = await test_session.get(Vacancy, create_vacancy)

    finished = sync_vacancy(vacancy)
    assert finished.status == "succeeded", finished.error

    document = meili.index("vacancies").get_document(vacancy.id)

    assert document.title == vacancy.title
    assert document.city == vacancy.city
    assert document.compensation == vacancy.compensation
    assert document.tenant_id == vacancy.tenant_id