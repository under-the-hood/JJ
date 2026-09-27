import pytest


@pytest.mark.asyncio
async def test_delete_invitation(admin_client, send_interview_invitation):
    invitation_id = await send_interview_invitation()

    response = await admin_client.request("DELETE", f"/invitations/{invitation_id}")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_set_status_as_admin(admin_client, send_interview_invitation):
    invitation_id = await send_interview_invitation()
    status = {
        "status": "accepted"
    }

    response = await admin_client.patch(f"/invitations/{invitation_id}/status", json=status)
    assert response.status_code == 403
