import pytest


@pytest.mark.asyncio
async def test_get_users(admin_client):

    response = await admin_client.get("/admin/users")

    assert response.status_code == 200

    data = response.json()

    assert data["quantity of all users"] > 0

    emails = [user["email"] for user in data["users"]]
    assert "admin_account@example.com" in emails


@pytest.mark.order(after="tests/test_users.py::test_get_info_about_user")
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