import pytest


@pytest.mark.asyncio
async def test_get_vacancies(admin_client, create_vacancy):

    response = await admin_client.get("/admin/vacancies")

    assert response.status_code == 200

    data = response.json()

    assert data["total"] > 0

    vacancies = [vacancy["title"] for vacancy in data["vacancies"]]
    assert "Python developer" in vacancies


@pytest.mark.asyncio
async def test_update_vacancy(admin_client, create_vacancy):

    vacancy_id = create_vacancy

    updated_vacancy = {
        "new_title": "FastAPI Developer",
        "new_compensation": 550000,
        "new_city": "Astana"
    }
    
    response = await admin_client.patch(f"/admin/vacancies/{vacancy_id}", json=updated_vacancy)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_vacancy(admin_client, create_vacancy):

    vacancy_id = create_vacancy

    response = await admin_client.request("DELETE", f"/admin/vacancies/{vacancy_id}")

    assert response.status_code == 200