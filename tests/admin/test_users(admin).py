import pytest

from app.backend.models.user import User
from app.backend.utils.search import sync_user


@pytest.mark.asyncio
async def test_search_users(admin_client, applicant_client, test_session):
    user_for_search = {
        "email": "user_for_search@example.com",
        "password": "password",
        "repeat_password": "password",
        "role": "applicant",
        "name": "FindMe"
    }

    user_response = await applicant_client.post("/users/sign_up", json=user_for_search)
    assert user_response.status_code == 200

    user_id = user_response.json()["user"]["id"]
    user = await test_session.get(User, user_id)
    sync_user(user)

    search_response = await admin_client.get("/admin/users")
    assert search_response.status_code == 200

    data = search_response.json()
    data = data["users"]

    emails = [email["email"] for email in data]
    assert "user_for_search@example.com" in emails


@pytest.mark.asyncio
async def test_update_user(admin_client, applicant_client):
    user_info = await applicant_client.get("/users/me")
    user_id = user_info.json()["info"]["id"]

    updated_user = {
        "new_name": "Artur",
        "new_role": "tenant"
    }

    response = await admin_client.patch(f"admin/users/{user_id}", json=updated_user)

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

    user_id = user_response.json()["user"]["id"]
    response = await admin_client.request("DELETE", f"/admin/users/{user_id}")

    assert response.status_code == 200