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
async def test_set_status(applicant_client, send_interview_invitation):
    invitation_id = await send_interview_invitation()

    status = {
        "status": "accepted"
    }

    response = await applicant_client.patch(f"/invitations/{invitation_id}/status", json=status)
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


@pytest.mark.asyncio
async def test_send_interview_invitation_duplicate(tenant_client, create_resume, valid_invitation_payload):
    first_invitation = await tenant_client.post(f"/invitations/interview/{create_resume}", json=valid_invitation_payload)
    assert first_invitation.status_code == 200

    second_invitation = await tenant_client.post(f"/invitations/interview/{create_resume}", json=valid_invitation_payload)
    assert second_invitation.status_code == 400


@pytest.mark.asyncio
async def test_send_interview_invitation_as_not_vacancy_owner(second_tenant_client, create_resume, valid_invitation_payload):
    response = await second_tenant_client.post(f"/invitations/interview/{create_resume}", json=valid_invitation_payload)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_send_interview_invitation_as_not_tenant(applicant_client, create_resume, valid_invitation_payload):
    response = await applicant_client.post(f"/invitations/interview/{create_resume}", json=valid_invitation_payload)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_invitation_as_not_owner(send_interview_invitation, second_tenant_client):
    invitation_id = await send_interview_invitation()

    response = await second_tenant_client.request("DELETE", f"/invitations/{invitation_id}")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_set_status_as_not_owner(send_interview_invitation, second_applicant_client):
    status = {
        "status": "accepted"
    }
    invitation_id = await send_interview_invitation()

    response = await second_applicant_client.patch(f"/invitations/{invitation_id}/status", json=status)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_send_interview_invitation_resume_not_found(tenant_client, valid_invitation_payload):
    resume_id = 99999

    response = await tenant_client.post(f"/invitations/interview/{resume_id}", json=valid_invitation_payload)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_send_interview_invitation_without_auth(client, create_resume, valid_invitation_payload):
    response = await client.post(f"/invitations/interview/{create_resume}", json=valid_invitation_payload)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_set_invalid_status(applicant_client, send_interview_invitation):
    status = {
        "status": "invalid status"
    }
    invitation_id = await send_interview_invitation()

    response = await applicant_client.patch(f"/invitations/{invitation_id}/status", json=status)
    assert response.status_code == 422
