import pytest

from app.backend.models.user import User
from app.backend.utils.meilisearch.user import sync_user
from tests.fixtures.users import get_id


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
async def test_update_user(admin_client, applicant_client, valid_update_user_payload):
    user_id = await get_id(applicant_client)

    response = await admin_client.patch(f"admin/users/{user_id}", json=valid_update_user_payload)
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


@pytest.mark.asyncio
async def test_update_user_as_not_admin(applicant_client, valid_update_user_payload):
    user_id = await get_id(applicant_client)

    response = await applicant_client.patch(f"/admin/users/{user_id}", json=valid_update_user_payload)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_user_as_not_admin(applicant_client):
    user_id = await get_id(applicant_client)

    response = await applicant_client.request("DELETE", f"/admin/users/{user_id}")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_update_self(admin_client, valid_update_user_payload):
    user_id = await get_id(admin_client)

    response = await admin_client.patch(f"/admin/users/{user_id}", json=valid_update_user_payload)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_delete_self(admin_client):
    user_id = await get_id(admin_client)

    response = await admin_client.request("DELETE", f"/admin/users/{user_id}")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_update_other_admin(admin_client, second_admin_client, valid_update_user_payload):
    admin_id = await get_id(admin_client)

    response = await second_admin_client.patch(f"/admin/users/{admin_id}", json=valid_update_user_payload)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_delete_other_admin(admin_client, second_admin_client):
    admin_id = await get_id(admin_client)

    response = await second_admin_client.request("DELETE", f"/admin/users/{admin_id}")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_nonexistent_user(admin_client, valid_update_user_payload):
    user_id = 99999
    
    response = await admin_client.patch(f"/admin/users/{user_id}", json=valid_update_user_payload)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_nonexistent_user(admin_client):
    user_id = 99999

    response = await admin_client.request("DELETE", f"/admin/users/{user_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_user_without_auth(client, applicant_client, valid_update_user_payload):
    user_id = await get_id(applicant_client)

    response = await client.patch(f"/admin/users/{user_id}", json=valid_update_user_payload)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_user_without_auth(client, applicant_client):
    user_id = await get_id(applicant_client)

    response = await client.request("DELETE", f"/admin/users/{user_id}")
    assert response.status_code == 401