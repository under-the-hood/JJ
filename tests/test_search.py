import pytest

from app.backend.models.resume import Resume
from app.backend.models.vacancy import Vacancy
from app.backend.utils.search import sync_vacancy, sync_resume


@pytest.mark.asyncio
async def test_search_resumes(tenant_client, create_resume, test_session):

    resume = await test_session.get(Resume, create_resume)
    sync_resume(resume)

    response = await tenant_client.get("/search/resumes")

    assert response.status_code == 200

    data = response.json()
    data = data["resumes"]

    assert isinstance(data, list)
    assert len(data) > 0

    titles = [resume["title"] for resume in data]
    assert "FastAPI Developer" in titles


@pytest.mark.asyncio
async def test_search_vacancies(applicant_client, create_vacancy, test_session):

    vacancy = await test_session.get(Vacancy, create_vacancy)
    sync_vacancy(vacancy)

    response = await applicant_client.get("/search/vacancies")

    assert response.status_code == 200

    data = response.json()
    data = data["vacancies"]

    assert isinstance(data, list)
    assert len(data) > 0

    titles = [vacancy["title"] for vacancy in data]
    assert "Python developer" in titles