import pytest

@pytest.fixture
async def create_vacancy(tenant_client):

    new_vacancy = {
        "title": "Python developer",
        "compensation": 500000,
        "city": "Almaty"
    }

    response = await tenant_client.post("/vacancies", json=new_vacancy)

    data = response.json()
    assert "vacancy" in data, data
    vacancy_id = data["vacancy"]["id"]    

    return vacancy_id