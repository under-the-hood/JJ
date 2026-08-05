import pytest


@pytest.mark.asyncio
async def test_search_resumes(tenant_client, create_resume):

    response = await tenant_client.get("/search/resumes")

    assert response.status_code == 200

    data = response.json()
    data = data["resumes"]

    assert isinstance(data, list)
    assert len(data) > 0

    titles = [resume["title"] for resume in data]
    assert "FastAPI Developer" in titles


@pytest.mark.asyncio
async def test_search_vacancies(applicant_client, create_vacancy):

    response = await applicant_client.get("/search/vacancies")

    assert response.status_code == 200

    data = response.json()
    data = data["vacancies"]

    assert isinstance(data, list)
    assert len(data) > 0

    titles = [vacancy["title"] for vacancy in data]
    assert "Python developer" in titles