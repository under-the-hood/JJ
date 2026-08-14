import pytest


@pytest.mark.asyncio
async def test_get_responses(admin_client, send_response_to_vacancy):

    await send_response_to_vacancy()
    response = await admin_client.get("/admin/responses")

    assert response.status_code == 200

    data = response.json()

    assert data["total"] > 0

    responses = [response["cover_letter"] for response in data["responses"]]
    assert "Hello! I want work in your company!" in responses


@pytest.mark.asyncio
async def test_delete_response(admin_client, send_response_to_vacancy):

    response_id = await send_response_to_vacancy()

    response = await admin_client.request("DELETE", f"/admin/responses/{response_id}")

    assert response.status_code == 200