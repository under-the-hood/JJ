import pytest
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.backend.models.mails import Mails
from app.backend.utils.meilisearch.response import sync_response
from app.backend.models.response import Response


@pytest.mark.asyncio
async def test_send_response_to_vacancy(send_response_to_vacancy, send_mail, test_session):
    send_mail.reset_mock()
    response_id = await send_response_to_vacancy()
    assert response_id is not None

    send_mail.assert_called_once()

    args, _ = send_mail.call_args
    mail_id = args[0]

    mail = await test_session.get(Mails, mail_id)
    assert mail.subject == "New response to your vacancy!"
    assert "city: Almaty" in mail.body


@pytest.mark.asyncio
async def test_search_responses(admin_client, tenant_client, send_response_to_vacancy, create_vacancy, test_session):
    response_id = await send_response_to_vacancy()
    query = await test_session.execute(
        select(Response)
        .options(joinedload(Response.resume))
        .where(Response.id == response_id)
    )
    response_to_vacancy = query.scalar_one()
    sync_response(response_to_vacancy)

    async def assert_response(client, params=None):
        response = await client.get("/responses", params=params)
        assert response.status_code == 200

        data = response.json()["responses"]
        titles = [response["resume"]["title"] for response in data]
        assert "FastAPI Developer" in titles

    await assert_response(admin_client)
    await assert_response(tenant_client, params={"vacancy_id": create_vacancy})


@pytest.mark.asyncio
async def test_delete_response(applicant_client, send_response_to_vacancy):
    response_id = await send_response_to_vacancy()

    response = await applicant_client.request("DELETE", f"/responses/{response_id}")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_set_status(tenant_client, send_response_to_vacancy):

    response_id = await send_response_to_vacancy()

    status = {
        "status": "hired"
    }

    response = await tenant_client.patch(f"/responses/{response_id}/status", json=status)

    assert response.status_code == 200