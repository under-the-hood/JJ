import pytest
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.backend.models.mails import Mails
from app.backend.utils.search import sync_response
from app.backend.models.response import Response


@pytest.mark.asyncio
async def test_send_response_to_vacancy(send_response_to_vacancy, send_mail, test_session):
    response = await send_response_to_vacancy()
    assert response is not None

    send_mail.assert_called_once()

    args, _ = send_mail.call_args
    mail_id = args[0]

    mail = await test_session.get(Mails, mail_id)
    assert mail.subject == "New response to your vacancy!"
    assert "city: Almaty" in mail.body


@pytest.mark.asyncio
async def test_get_responses(tenant_client, create_vacancy, send_response_to_vacancy):

    await send_response_to_vacancy()
    vacancy_id = create_vacancy

    response = await tenant_client.get(f"/responses/vacancies/{vacancy_id}")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0

    first_response = data[0]
    assert "resume" in first_response
    assert "user" in first_response


@pytest.mark.asyncio
async def test_search_responses(admin_client, send_response_to_vacancy, test_session):
    response_id = await send_response_to_vacancy()

    query = await test_session.execute(
        select(Response)
        .options(joinedload(Response.resume))
        .where(Response.id == response_id)
    )
    response_to_vacancy = query.scalar_one()
    sync_response(response_to_vacancy)

    search_response = await admin_client.get("/responses")
    assert search_response.status_code == 200

    data = search_response.json()["responses"][0]["resume"]["title"]
    assert "FastAPI Developer" in data


@pytest.mark.asyncio
async def test_set_status(tenant_client, send_response_to_vacancy):

    response_id = await send_response_to_vacancy()

    status = {
        "status": "hired"
    }

    response = await tenant_client.patch(f"/responses/{response_id}/status", json=status)

    assert response.status_code == 200