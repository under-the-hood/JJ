import pytest


@pytest.mark.asyncio
async def test_create_vacancy(create_vacancy):
    assert create_vacancy is not None


@pytest.mark.asyncio
async def test_get_all_my_vacancies(tenant_client):

    response = await tenant_client.get("/vacancy/get_all_my_vacancies")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data["Your vacancies"], list)
    assert len(data["Your vacancies"]) > 0
    assert data["Your vacancies"][0]["title"] == "Python developer"


@pytest.mark.asyncio
async def test_edit_vacancy(tenant_client, create_vacancy):

    vacancy_id = create_vacancy

    edited_vacancy = {
        "vacancy_id": vacancy_id,
        "new_title": "FastAPI Developer",
        "new_compensation": 550000,
        "new_city": "Astana"
    }

    response = await tenant_client.put(f"/vacancy/edit_vacancy/{vacancy_id}", params=edited_vacancy)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_vacancy(tenant_client, create_vacancy):

    vacancy_id = create_vacancy

    response = await tenant_client.request("DELETE", f"/vacancy/delete_vacancy/{vacancy_id}")

    assert response.status_code == 200