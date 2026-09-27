import pytest


@pytest.fixture(autouse=True)
def sync_user(mocker):
    return mocker.patch("app.backend.helpers.celery_tasks.meilisearch.user.sync_user_task.delay")

@pytest.fixture(autouse=True)
def delete_user(mocker):
    return mocker.patch("app.backend.helpers.celery_tasks.meilisearch.user.delete_user_task.delay")


@pytest.fixture
def valid_user_payload():
    return {
            "email": "new_account@example.com",
            "name": "Someone",
            "password": "12345678",
            "repeat_password": "12345678",
            "role": "tenant"
        }

@pytest.fixture
def valid_update_user_payload():
    return {
        "new_name": "Artur",
        "new_role": "tenant"
    }


async def get_id(client):
    response = await client.get("/users/me")
    return response.json()["info"]["id"]