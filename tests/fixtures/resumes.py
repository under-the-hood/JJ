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