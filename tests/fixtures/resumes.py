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
    assert "Resume" in data, data
    resume_id = data["Resume"]["id"]

    return resume_id