import pytest


@pytest.mark.asyncio
async def test_create_resume(create_resume):
    assert create_resume is not None


@pytest.mark.asyncio
async def test_get_my_resumes(applicant_client):

    response = await applicant_client.get("/resumes/my")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data["Your resumes"], list)
    assert len(data["Your resumes"]) > 0
    assert data["Your resumes"][0]["title"] == "FastAPI Developer"


@pytest.mark.asyncio
async def test_edit_resume(applicant_client, create_resume):
    resume_id = create_resume

    edited_resume = {
        "resume_id": resume_id,
        "new_title": "Junior FastAPI Developer",
        "new_about": "Im a FastAPI developer",
        "new_city": "Astana",
        "stack": "FastAPI, PostgreSQL, Python, Docker"
    }

    response = await applicant_client.put(f"/resumes/{resume_id}", json=edited_resume)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_resume(applicant_client, create_resume):
    resume_id = create_resume

    response = await applicant_client.request("DELETE", f"/resumes/{resume_id}")

    assert response.status_code == 200