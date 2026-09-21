import pytest


@pytest.mark.asyncio
async def test_create_resume(create_resume):
    assert create_resume is not None


@pytest.mark.asyncio
async def test_get_my_resumes(applicant_client, create_resume):

    response = await applicant_client.get("/resumes/my")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data["resumes"], list)
    assert len(data["resumes"]) > 0
    assert data["resumes"][0]["title"] == "FastAPI Developer"


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


@pytest.mark.asyncio
async def test_create_resume_as_tenant(tenant_client, valid_resume_payload):
    response = await tenant_client.post("/resumes", json=valid_resume_payload)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_resume_as_not_owner(second_applicant_client, create_resume):
    upadted_resume = {
        "new_title": "Python Dev"
    }

    update_other_resume = await second_applicant_client.patch(f"/resumes/{create_resume}", json=upadted_resume)
    assert update_other_resume.status_code == 403


@pytest.mark.asyncio
async def test_delete_resume_as_not_owner(second_applicant_client, create_resume):
    delete_other_resume = await second_applicant_client.request("DELETE", f"/resumes/{create_resume}")
    assert delete_other_resume.status_code == 403


@pytest.mark.asyncio
async def test_update_nonexistent_resume(applicant_client):
    resume_id = 999999999

    upadted_resume = {
        "new_title": "Python Dev"
    }

    response = await applicant_client.patch(f"/resumes/{resume_id}", json=upadted_resume)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_nonexistent_resume_404(applicant_client):
    resume_id = 999999999

    response = await applicant_client.request("DELETE", f"/resumes/{resume_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_resume_without_auth(client, valid_resume_payload):
    response = await client.post("/resumes", json=valid_resume_payload)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_resume_with_invalid_fields(applicant_client):
    new_resume = {
        "title": "py",
        "about": "I'm a <>junior FastAPI developer",
        "city": "Almaty<>",
        "stack": "FastAPI, PostgreSQL, Python><|"
    }

    response = await applicant_client.post("/resumes", json=new_resume)
    assert response.status_code == 422
