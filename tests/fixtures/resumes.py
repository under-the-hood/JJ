import pytest

@pytest.fixture
async def create_resume(applicant_client):

    new_resume = {
        "title": "FastAPI Developer",
        "about": "Im a junior FastAPI developer",
        "city": "Almaty",
        "stack": "FastAPI, PostgreSQL, Python"
    }

    response = await applicant_client.post("/resumes", json=new_resume)

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