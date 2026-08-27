import pytest


@pytest.mark.anyio
async def search_users():
    ...


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

    users_query = await admin_client.get("/admin/users")
    users = users_query.json()["users"]
    user_id = next(u["id"] for u in users if u["email"] == "user_for_delete@example.com")

    response = await admin_client.request("DELETE", f"/admin/users/{user_id}")

    assert response.status_code == 200