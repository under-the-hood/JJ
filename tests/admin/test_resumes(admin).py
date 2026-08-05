import pytest


@pytest.mark.asyncio
async def test_get_resumes(admin_client, create_resume):

    response = await admin_client.get("/admin/resumes")

    assert response.status_code == 200

    data = response.json()

    assert data["quantity of all resumes"] > 0

    resumes = [resume["title"] for resume in data["resumes"]]
    assert "FastAPI Developer" in resumes


@pytest.mark.asyncio
async def test_update_resume(admin_client, create_resume):

    resume_id = create_resume

    edited_resume = {
        "resume_id": resume_id,
        "new_title": "Junior FastAPI Developer",
        "new_about": "Im a FastAPI developer",
        "new_city": "Astana",
        "stack": "FastAPI, PostgreSQL, Python, Docker"
    }

    response = await admin_client.patch(f"/admin/resumes/{resume_id}", json=edited_resume)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_resume(admin_client, create_resume):

    resume_id = create_resume

    response = await admin_client.request("DELETE", f"/admin/resumes/{resume_id}")

    assert response.status_code == 200