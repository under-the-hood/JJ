import pytest
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.backend.models.invitations import Invitation
from app.backend.utils.meilisearch.invitation import sync_invitation

@pytest.mark.asyncio
async def test_send_interview_invitation(send_interview_invitation):
    invitation_id = await send_interview_invitation()
    assert invitation_id is not None


@pytest.mark.asyncio
async def test_delete_invitation(tenant_client, send_interview_invitation):
    invitation_id = await send_interview_invitation()

    response = await tenant_client.request("DELETE", f"/invitations/{invitation_id}")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_search_invitations(admin_client, tenant_client, applicant_client, send_interview_invitation, test_session, create_vacancy, create_resume):
    invitation_id = await send_interview_invitation()
    
    query = await test_session.execute(
        select(Invitation)
        .options(joinedload(Invitation.resume), joinedload(Invitation.vacancy))
        .where(Invitation.id == invitation_id)
    )
    invitation = query.scalar_one()
    sync_invitation(invitation)

    async def assert_invitation(client):
        response = await client.get("/invitations")
        assert response.status_code == 200

        data = response.json()["invitations"]
        resume_titles = [invitation["resume_title"] for invitation in data]
        assert "FastAPI Developer" in resume_titles

    await assert_invitation(admin_client)
    await assert_invitation(tenant_client)
    await assert_invitation(applicant_client)