import pytest
from sqlalchemy import select

from backend.models.models import ResumeModel


@pytest.mark.anyio
async def test_create_resume(create_resume):
    assert create_resume is not None


@pytest.mark.anyio
async def test_get_all_my_resumes(get_token_as_applicant):

    response = await get_token_as_applicant.get("/resume/get_all_my_resumes")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data["Your resumes"], list)
    assert len(data["Your resumes"]) > 0
    assert data["Your resumes"][0]["title"] == "FastAPI Developer"


@pytest.mark.anyio
async def test_edit_resume(get_token_as_applicant, create_resume):

    resume_id = create_resume

    edited_resume = {
        "resume_id": resume_id,
        "new_title": "Junior FastAPI Developer",
        "new_about": "Im a FastAPI developer",
        "new_city": "Astana",
        "stack": "FastAPI, PostgreSQL, Python, Docker"
    }

    response = await get_token_as_applicant.put(f"/resume/edit_resume/{resume_id}", json=edited_resume)

    assert response.status_code == 200


@pytest.mark.anyio
async def test_delete_resume(get_token_as_applicant, create_resume):

    resume_id = create_resume

    response = await get_token_as_applicant.request("DELETE", f"/resume/delete_resume/{resume_id}")

    assert response.status_code == 200