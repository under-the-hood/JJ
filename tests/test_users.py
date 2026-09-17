import pytest


@pytest.mark.asyncio
async def test_create_user(tenant_client):
    assert tenant_client.headers.get("Authorization") is not None


@pytest.mark.asyncio
async def test_get_info_about_user(tenant_client):
    response = await tenant_client.get("/users/me")

    assert response.status_code == 200

    data = response.json()

    assert data["info"]["email"] == "tenant_account@example.com"
    assert isinstance(data["info"]["id"], int)


@pytest.mark.asyncio
async def test_update_password(tenant_client):
    new_password = {
        "old_password": "12345678",
        "new_password": "12345678",
        "repeat_new_password": "12345678"
    }

    response = await tenant_client.patch("/users/me/password", json=new_password)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_name(tenant_client):
    new_name = {
        "new_name": "Andrey"
    }

    response = await tenant_client.patch("/users/me/name", json=new_name)

    assert response.status_code == 200


@pytest.mark.order(-1)
async def test_delete_user(tenant_client):
    confirm_password = {
        "password": "12345678"
    }

    response = await tenant_client.request("DELETE", "/users/me", json=confirm_password)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_sign_up_with_existing_email(client, valid_user_payload):
    first_response = await client.post("/users/sign_up", json=valid_user_payload)
    assert first_response.status_code == 200

    second_response = await client.post("/users/sign_up", json=valid_user_payload)
    assert second_response.status_code == 409


@pytest.mark.asyncio
async def test_sign_up_with_mismatched_passwords(client, valid_user_payload):
    new_user = {
        **valid_user_payload,
        "repeat_password": "123456789"
    }

    response = await client.post("/users/sign_up", json=new_user)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_sign_up_with_invalid_email(client, valid_user_payload):
    new_user = {
        **valid_user_payload,
        "email": "--new_account@example.com--"
    }

    response = await client.post("/users/sign_up", json=new_user)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_sign_up_with_too_short_password(client, valid_user_payload):
    new_user = {
        **valid_user_payload,
        "password": "123",
        "repeat_password": "123"
    }

    response = await client.post("/users/sign_up", json=new_user)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_sign_in_with_wrong_password(client):
    sign_in = {
        "email": "applicant_account@example.com",
        "password": "wrong_password"
    }

    response = await client.post("/users/sign_in", json=sign_in)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_sign_in_with_nonexistent_email(client):
    sign_in = {
        "email": "nonexistent_email@example.com",
        "password": "12345678"
    }

    response = await client.post("/users/sign_in", json=sign_in)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_without_auth(client):
    response = await client.get("/users/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_password_with_wrong_old_password(applicant_client):
    update_password = {
        "old_password": "wrong_old_password",
        "new_password": "123456789",
        "repeat_new_password": "123456789"
    }

    response = await applicant_client.patch("/users/me/password", json=update_password)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_update_password_with_mismatched_new_passwords(applicant_client):
    update_password = {
        "old_password": "12345678",
        "new_password": "new_password",
        "repeat_new_password": "mismatched_new_password"
    }

    response = await applicant_client.patch("/users/me/password", json=update_password)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_delete_user_with_wrong_password(applicant_client):
    confirm_password = {
        "password": "wrong_password"
    }

    response = await applicant_client.request("DELETE", "/users/me", json=confirm_password)
    assert response.status_code == 400
