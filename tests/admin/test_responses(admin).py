import pytest


@pytest.mark.asyncio
async def test_delete_response(admin_client, send_response_to_vacancy):

    response_id = await send_response_to_vacancy()

    response = await admin_client.request("DELETE", f"/admin/responses/{response_id}")

    assert response.status_code == 200