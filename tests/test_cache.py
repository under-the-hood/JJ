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
async def test_cache_invalidation_on_vacancy_update(send_response_to_vacancy, tenant_client, applicant_client, create_vacancy):
    await send_response_to_vacancy()

    await applicant_client.get("/responses/my")
    first_response = await applicant_client.get("/responses/my")

    assert first_response.json()["source"] == "cache"

    updated_vacancy = {
        "new_title": "FastAPI Developer"
    }

    update_title = await tenant_client.patch(f"/vacancies/{create_vacancy}", json=updated_vacancy)
    assert update_title.status_code == 200

    second_response = await applicant_client.get("/responses/my")
    data = second_response.json()

    assert data["source"] == "db"
    assert data["responses"][0]["vacancy"]["title"] == "FastAPI Developer"