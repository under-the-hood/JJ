import pytest


@pytest.mark.asyncio
async def test_create_user(tenant_client):
    assert tenant_client.headers.get("Authorization") is not None


@pytest.mark.asyncio
async def test_get_info_about_user(tenant_client):

    response = await tenant_client.get("/user/get_info")

    assert response.status_code == 200

    data = response.json()

    assert data["info"]["email"] == "tenant_account@example.com"
    assert isinstance(data["info"]["id"], int)


@pytest.mark.asyncio
async def test_edit_password(tenant_client):

    new_password = {
        "old_password": "12345678",
        "new_password": "12345678",
        "repeat_new_password": "12345678"
    }

    response = await tenant_client.put("/user/edit_password", json=new_password)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_edit_name(tenant_client):
        
    new_name = {
        "new_name": "Andrey"
    }

    response = await tenant_client.put("/user/edit_name", json=new_name)

    assert response.status_code == 200


@pytest.mark.order(-1)
async def test_delete_user(tenant_client):

    confirm_password = {
        "password": "12345678"
    }

    response = await tenant_client.request("DELETE", "/user/delete_user", json=confirm_password)

    assert response.status_code == 200