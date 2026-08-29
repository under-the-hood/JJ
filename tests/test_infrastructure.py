import pytest

@pytest.mark.asyncio
async def test_user_info_cache_invalidation(tenant_client):

    await tenant_client.get("/users/me")
    first_response = await tenant_client.get("/users/me")

    data = first_response.json()
    assert data["source"] == "cache"

    new_name = {
        "new_name": "Anton"
    }

    await tenant_client.patch("/users/me/name", json=new_name)

    second_response = await tenant_client.get("/users/me")
    
    data = second_response.json()
    assert data["source"] == "db"