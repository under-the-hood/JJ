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


@pytest.fixture(autouse=True)
def sync_vacancy(mocker):
    return mocker.patch("app.backend.helpers.celery_tasks.meilisearch.vacancy.sync_vacancy_task.delay")

@pytest.fixture(autouse=True)
def delete_vacancy(mocker):
    return mocker.patch("app.backend.helpers.celery_tasks.meilisearch.vacancy.delete_vacancy_task.delay")