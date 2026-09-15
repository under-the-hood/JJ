import pytest


@pytest.fixture
def valid_resume_payload():
    return {
        "title": "FastAPI Developer",
        "about": "Im a junior FastAPI developer",
        "city": "Almaty",
        "stack": "FastAPI, PostgreSQL, Python"
    }


@pytest.fixture
async def create_resume(applicant_client, valid_resume_payload):
    response = await applicant_client.post("/resumes", json=valid_resume_payload)

    data = response.json()
    assert "resume" in data, data
    resume_id = data["resume"]["id"]

    return resume_id


@pytest.fixture(autouse=True)
def sync_resume(mocker):
    return mocker.patch("app.backend.helpers.celery_tasks.meilisearch.resume.sync_resume_task.delay")

@pytest.fixture(autouse=True)
def delete_resume(mocker):
    return mocker.patch("app.backend.helpers.celery_tasks.meilisearch.resume.delete_resume_task.delay")
