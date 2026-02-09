import pytest


#Test admin role for work with users
@pytest.mark.anyio
async def test_get_users(get_token_as_admin):

    response = await get_token_as_admin.get("/admin/get_users")

    assert response.status_code == 200

    data = response.json()

    assert data["quantity of all users"] > 0

    emails = [user["email"] for user in data["users"]]
    assert "admin_account@example.com" in emails


@pytest.mark.order(after="tests/test_user.py::test_get_info_about_user")
async def test_edit_user_name(get_token_as_admin):

    users_query = await get_token_as_admin.get("/admin/get_users")
    users = users_query.json()["users"]
    user_id = next(u["id"] for u in users if u["role"] != "admin")

    new_name = {
        "user_id": user_id,
        "new_name": "Artur"
    }

    response = await get_token_as_admin.put(f"/admin/edit_user_name/{user_id}", json=new_name)

    assert response.status_code == 200


@pytest.mark.order(after="tests/test_user.py::test_get_info_about_user")
async def test_update_user_role(get_token_as_admin):

    users_query = await get_token_as_admin.get("/admin/get_users")
    users = users_query.json()["users"]
    user_id = next(u["id"] for u in users if u["role"] != "admin")

    new_role = {
        "user_id": user_id,
        "new_role": "tenant"
    }

    response = await get_token_as_admin.put(f"/admin/update_user_role/{user_id}", json=new_role)

    assert response.status_code == 200


@pytest.mark.anyio
async def test_delete_user_as_admin(get_token_as_admin, get_token_as_applicant):

    user_for_delete = {
        "email": "user_for_delete@example.com",
        "password": "password",
        "repeat_password": "password",
        "role": "applicant",
        "name": "DeleteMe"
    }

    user_response = await get_token_as_applicant.post("/user/sign_up", json=user_for_delete)
    assert user_response.status_code == 200

    users_query = await get_token_as_admin.get("/admin/get_users")
    users = users_query.json()["users"]
    user_id = next(u["id"] for u in users if u["email"] == "user_for_delete@example.com")

    response = await get_token_as_admin.request("DELETE", f"/admin/delete_user/{user_id}")

    assert response.status_code == 200


#Test admin role for work with vacancy
@pytest.mark.anyio
async def test_edit_vacancy_as_admin(get_token_as_admin, create_vacancy):

    vacancy_id = create_vacancy

    edited_vacancy = {
        "vacancy_id": vacancy_id,
        "new_title": "FastAPI Developer",
        "new_compensation": 550000,
        "new_city": "Astana"
    }
    
    response = await get_token_as_admin.put(f"/admin/edit_vacancy/{vacancy_id}", json=edited_vacancy)

    assert response.status_code == 200


@pytest.mark.anyio
async def test_get_vacancies(get_token_as_admin):

    response = await get_token_as_admin.get("/admin/get_vacancies")

    assert response.status_code == 200

    data = response.json()

    assert data["quantity of all vacancies"] > 0

    vacancies = [vacancy["title"] for vacancy in data["vacancies"]]
    assert "Python developer" in vacancies


@pytest.mark.anyio
async def test_delete_vacancy_as_admin(get_token_as_admin, create_vacancy):

    vacancy_id = create_vacancy

    response = await get_token_as_admin.request("DELETE", f"/admin/delete_vacancy/{vacancy_id}")

    assert response.status_code == 200


#Test admin role for work with resume
@pytest.mark.anyio
async def test_edit_resume_as_admin(get_token_as_admin, create_resume):

    resume_id = create_resume

    edited_resume = {
        "resume_id": resume_id,
        "new_title": "Junior FastAPI Developer",
        "new_about": "Im a FastAPI developer",
        "new_city": "Astana",
        "stack": "FastAPI, PostgreSQL, Python, Docker"
    }

    response = await get_token_as_admin.put(f"/admin/edit_resume/{resume_id}", json=edited_resume)

    assert response.status_code == 200


@pytest.mark.anyio
async def test_get_resumes(get_token_as_admin):

    response = await get_token_as_admin.get("/admin/get_resumes")

    assert response.status_code == 200

    data = response.json()

    assert data["quantity of all resumes"] > 0

    resumes = [resume["title"] for resume in data["resumes"]]
    assert "FastAPI Developer" in resumes


@pytest.mark.anyio
async def test_delete_resume_as_admin(get_token_as_admin, create_resume):

    resume_id = create_resume

    response = await get_token_as_admin.request("DELETE", f"/admin/delete_resume/{resume_id}")

    assert response.status_code == 200


#Test admin role for work with response
@pytest.mark.anyio
async def test_get_responses_as_admin(get_token_as_admin, apply_to_vacancy):

    response = await get_token_as_admin.get("/admin/get_responses")

    assert response.status_code == 200

    data = response.json()

    assert data["quantity of all responses"] > 0

    responses = [response["cover_letter"] for response in data["responses"]]
    assert "Hello! I want work in your company!" in responses


@pytest.mark.anyio
async def test_delete_response(get_token_as_admin, apply_to_vacancy):

    response_id = apply_to_vacancy

    response = await get_token_as_admin.request("DELETE", f"/admin/delete_response/{response_id}")

    assert response.status_code == 200