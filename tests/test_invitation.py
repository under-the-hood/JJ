import pytest

@pytest.mark.asyncio
async def test_send_interview_invitation(send_interview_invitation):
    invitation_id = await send_interview_invitation()
    assert invitation_id is not None


@pytest.mark.asyncio
async def test_delete_invitation(tenant_client, send_interview_invitation):
    invitation_id = await send_interview_invitation()

    response = await tenant_client.request("DELETE", f"/invitation/{invitation_id}")
    assert response.status_code == 200