import pytest

@pytest.mark.asyncio
async def test_send_interview_invitation(send_interview_invitation):
    invitation_id = await send_interview_invitation()
    assert invitation_id is not None