import pytest


@pytest.mark.asyncio
async def test_create_resume(create_resume):
    assert create_resume is not None


@pytest.mark.asyncio
async def test_get_my_resumes(applicant_client, create_resume):

    response = await applicant_client.get("/resumes/my")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data["Your resumes"], list)
    assert len(data["Your resumes"]) > 0
    assert data["Your resumes"][0]["title"] == "FastAPI Developer"


@pytest.mark.asyncio
async def test_update_resume(applicant_client, create_resume):
    resume_id = create_resume

    updated_resume = {
        "new_title": "Junior FastAPI Developer",
        "new_about": "Im a FastAPI developer",
        "new_city": "Astana",
        "new_stack": "FastAPI, PostgreSQL, Python, Docker"
    }

    response = await applicant_client.patch(f"/resumes/{resume_id}", json=updated_resume)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_resume(applicant_client, create_resume):
    resume_id = create_resume

    response = await applicant_client.request("DELETE", f"/resumes/{resume_id}")

    assert response.status_code == 200