import pytest

@pytest.mark.asyncio
async def test_update_vacancy(admin_client, create_vacancy):

    vacancy_id = create_vacancy

    updated_vacancy = {
        "new_title": "FastAPI Developer",
        "new_compensation": 550000,
        "new_city": "Astana"
    }
    
    response = await admin_client.patch(f"/vacancies/{vacancy_id}", json=updated_vacancy)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_vacancy(admin_client, create_vacancy):

    vacancy_id = create_vacancy

    response = await admin_client.request("DELETE", f"/vacancies/{vacancy_id}")

    assert response.status_code == 200