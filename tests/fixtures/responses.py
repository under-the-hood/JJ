import pytest

@pytest.fixture
def send_response_to_vacancy(applicant_client, create_vacancy, create_resume):
    async def create_response():
        cover_letter = {
            "resume_id": create_resume,
            "cover_letter": "Hello! I want work in your company!",
        }

        response = await applicant_client.post(f"/responses/vacancies/{create_vacancy}", json=cover_letter)
        assert response.status_code == 200

        data = response.json()
        response_id = data["response"]["id"]

        return response_id
    return create_response


@pytest.fixture(autouse=True)
def sync_response(mocker):
    return mocker.patch("app.backend.helpers.celery_tasks.meilisearch.response.sync_response_task.delay")

@pytest.fixture(autouse=True)
def delete_response(mocker):
    return mocker.patch("app.backend.helpers.celery_tasks.meilisearch.response.delete_response_task.delay")