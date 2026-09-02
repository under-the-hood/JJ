import pytest

from app.backend.models.resume import Resume
from app.backend.models.vacancy import Vacancy
from app.backend.utils.meilisearch.vacancy import sync_vacancy
from app.backend.utils.meilisearch.resume import sync_resume


@pytest.mark.asyncio
async def test_search_resumes(tenant_client, admin_client, create_resume, test_session):

    resume = await test_session.get(Resume, create_resume)
    sync_resume(resume)

    async def assert_resume(client):
        response = await client.get("/search/resumes")
        assert response.status_code == 200

        data = response.json()
        data = data["resumes"]
        titles = [resume["title"] for resume in data]
        assert "FastAPI Developer" in titles

    await assert_resume(tenant_client)
    await assert_resume(admin_client)


@pytest.mark.asyncio
async def test_search_vacancies(applicant_client, admin_client, create_vacancy, test_session):
    vacancy = await test_session.get(Vacancy, create_vacancy)
    sync_vacancy(vacancy)

    async def assert_vacancy(client):
        response = await client.get("/search/vacancies")
        assert response.status_code == 200

        data = response.json()
        data = data["vacancies"]
        titles = [vacancy["title"] for vacancy in data]
        assert "Python developer" in titles

    await assert_vacancy(applicant_client)
    await assert_vacancy(admin_client)