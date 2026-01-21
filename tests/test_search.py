import pytest


@pytest.mark.anyio
async def test_resume_search(get_token_as_tenant):

    response = await get_token_as_tenant.get("/search/search_resumes")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0

    titles = [resume["title"] for resume in data]
    assert "FastAPI Developer" in titles


@pytest.mark.anyio
async def test_vacancy_search(get_token_as_applicant):

    response = await get_token_as_applicant.get("/search/search_vacancies")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0

    titles = [vacancy["title"] for vacancy in data]
    assert "Python developer" in titles