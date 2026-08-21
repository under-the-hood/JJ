import pytest


@pytest.mark.asyncio
async def test_create_vacancy(create_vacancy):
    assert create_vacancy is not None


@pytest.mark.asyncio
async def test_my_vacancies(tenant_client, create_vacancy):

    response = await tenant_client.get("/vacancies/my")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data["vacancies"], list)
    assert len(data["vacancies"]) > 0
    assert data["vacancies"][0]["title"] == "Python developer"


@pytest.mark.asyncio
async def test_update_vacancy(tenant_client, create_vacancy):

    vacancy_id = create_vacancy

    updated_vacancy = {
        "new_title": "FastAPI Developer",
        "new_compensation": 550000,
        "new_city": "Astana"
    }

    response = await tenant_client.patch(f"/vacancies/{vacancy_id}", json=updated_vacancy)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_vacancy(tenant_client, create_vacancy):

    vacancy_id = create_vacancy

    response = await tenant_client.request("DELETE", f"/vacancies/{vacancy_id}")

    assert response.status_code == 200