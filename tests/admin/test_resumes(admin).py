import pytest

@pytest.mark.asyncio
async def test_update_resume(admin_client, create_resume):
    resume_id = create_resume

    updated_resume = {
        "new_title": "Junior FastAPI Developer",
        "new_about": "Im a FastAPI developer",
        "new_city": "Astana",
        "new_stack": "FastAPI, PostgreSQL, Python, Docker"
    }

    response = await admin_client.patch(f"/resumes/{resume_id}", json=updated_resume)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_resume(admin_client, create_resume):

    resume_id = create_resume

    response = await admin_client.request("DELETE", f"/resumes/{resume_id}")

    assert response.status_code == 200