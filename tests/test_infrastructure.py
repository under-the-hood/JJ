import pytest


@pytest.mark.asyncio
async def test_user_info_cache_invalidation(tenant_client):

    await tenant_client.get("/users/me")
    first_response = await tenant_client.get("/users/me")

    data = first_response.json()
    assert data["source"] == "cache"

    new_name = {
        "new_name": "Anton"
    }

    await tenant_client.patch("/users/me/name", json=new_name)

    second_response = await tenant_client.get("/users/me")
    
    data = second_response.json()
    assert data["source"] == "db"


@pytest.mark.asyncio
async def test_vacancy_search_invalidation(applicant_client, tenant_client):

    first_response = await applicant_client.get("/search/vacancies")
    assert first_response.json()["source"] == "db"

    second_response = await applicant_client.get("/search/vacancies")
    assert second_response.json()["source"] == "cache"

    new_vacancy = {
        "title": "Senior Python Developer",
        "city": "Almaty",
        "compensation": 500000
    }

    await tenant_client.post("/vacancies", json=new_vacancy)

    third_response = await applicant_client.get("/search/vacancies")
    assert third_response.json()["source"] == "db"

    titles = [v["title"] for v in third_response.json()["vacancies"]]
    assert "Senior Python Developer" in titles