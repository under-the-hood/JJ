import pytest


@pytest.mark.anyio
async def test_create_user(get_token_as_tenant):
    assert get_token_as_tenant.headers.get("Authorization") is not None


@pytest.mark.anyio
async def test_get_info_about_user(get_token_as_tenant):

    response = await get_token_as_tenant.get("/user/get_info")

    assert response.status_code == 200

    data = response.json()

    assert data["info"]["email"] == "tenant_account@example.com"
    assert isinstance(data["info"]["id"], int)


@pytest.mark.anyio
async def test_edit_password(get_token_as_tenant):

    new_password = {
        "old_password": "12345678",
        "new_password": "12345678",
        "repeat_new_password": "12345678"
    }

    response = await get_token_as_tenant.put("/user/edit_password", json=new_password)

    assert response.status_code == 200


@pytest.mark.anyio
async def test_edit_name(get_token_as_tenant):
        
    new_name = {
        "new_name": "Andrey",
        "password": "12345678"
    }

    response = await get_token_as_tenant.put("/user/edit_name", json=new_name)

    assert response.status_code == 200


@pytest.mark.order(-1)
async def test_delete_user(get_token_as_tenant):

    confirm_password = {
        "password": "12345678"
    }

    response = await get_token_as_tenant.request("DELETE", "/user/delete_user", json=confirm_password)

    assert response.status_code == 200