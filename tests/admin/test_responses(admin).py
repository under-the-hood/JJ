import pytest


@pytest.mark.asyncio
async def test_delete_response(admin_client, send_response_to_vacancy):
    response_id = await send_response_to_vacancy()

    response = await admin_client.request("DELETE", f"/responses/{response_id}")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_set_status_as_admin(admin_client, send_response_to_vacancy):
    response_id = await send_response_to_vacancy()
    status = {
        "status": "hired"
    }

    response = await admin_client.patch(f"/responses/{response_id}/status", json=status)
    assert response.status_code == 403
