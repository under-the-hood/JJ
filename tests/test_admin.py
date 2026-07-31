import pytest


#Test admin role for work with users
@pytest.mark.asyncio
async def test_get_users(admin_client):

    response = await admin_client.get("/admin/users")

    assert response.status_code == 200

    data = response.json()

    assert data["quantity of all users"] > 0

    emails = [user["email"] for user in data["users"]]
    assert "admin_account@example.com" in emails


@pytest.mark.order(after="tests/test_user.py::test_get_info_about_user")
async def test_update_name(admin_client, tenant_client):
    user_info = await tenant_client.get("/users/me")
    user_id = user_info.json()["info"]["id"]

    new_name = {
        "new_name": "Artur"
    }

    response = await admin_client.patch(f"/admin/users/{user_id}/name", json=new_name)

    assert response.status_code == 200


@pytest.mark.order(after="tests/test_user.py::test_get_info_about_user")
async def test_update_role(admin_client, applicant_client):
    user_info = await applicant_client.get("/users/me")
    user_id = user_info.json()["info"]["id"]

    new_role = {
        "new_role": "tenant"
    }

    response = await admin_client.patch(f"/admin/users/{user_id}/role", json=new_role)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_user(admin_client, applicant_client):

    user_for_delete = {
        "email": "user_for_delete@example.com",
        "password": "password",
        "repeat_password": "password",
        "role": "applicant",
        "name": "DeleteMe"
    }

    user_response = await applicant_client.post("/users/sign_up", json=user_for_delete)
    assert user_response.status_code == 200

    users_query = await admin_client.get("/admin/users")
    users = users_query.json()["users"]
    user_id = next(u["id"] for u in users if u["email"] == "user_for_delete@example.com")

    response = await admin_client.request("DELETE", f"/admin/users/{user_id}")

    assert response.status_code == 200


#Test admin role for work with vacancy
@pytest.mark.asyncio
async def test_get_vacancies(admin_client, create_vacancy):

    response = await admin_client.get("/admin/vacancies")

    assert response.status_code == 200

    data = response.json()

    assert data["quantity of all vacancies"] > 0

    vacancies = [vacancy["title"] for vacancy in data["vacancies"]]
    assert "Python developer" in vacancies


@pytest.mark.asyncio
async def test_update_vacancy(admin_client, create_vacancy):

    vacancy_id = create_vacancy

    edited_vacancy = {
        "vacancy_id": vacancy_id,
        "new_title": "FastAPI Developer",
        "new_compensation": 550000,
        "new_city": "Astana"
    }
    
    response = await admin_client.patch(f"/admin/vacancies/{vacancy_id}", json=edited_vacancy)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_vacancy(admin_client, create_vacancy):

    vacancy_id = create_vacancy

    response = await admin_client.request("DELETE", f"/admin/vacancies/{vacancy_id}")

    assert response.status_code == 200


#Test admin role for work with resume
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


#Test admin role for work with response
@pytest.mark.asyncio
async def test_get_responses(admin_client, send_response_to_vacancy):

    response = await admin_client.get("/admin/responses")

    assert response.status_code == 200

    data = response.json()

    assert data["quantity of all responses"] > 0

    responses = [response["cover_letter"] for response in data["responses"]]
    assert "Hello! I want work in your company!" in responses


@pytest.mark.asyncio
async def test_delete_response(admin_client, send_response_to_vacancy):

    response_id = send_response_to_vacancy

    response = await admin_client.request("DELETE", f"/admin/responses/{response_id}")

    assert response.status_code == 200