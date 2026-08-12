import pytest

from app.backend.models.mails import Mails


@pytest.mark.asyncio
async def test_send_response_to_vacancy(send_response_to_vacancy, mock_celery, test_session):
    response = await send_response_to_vacancy()
    assert response is not None

    mock_celery.assert_called_once()

    args, _ = mock_celery.call_args
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
async def test_set_status(tenant_client, send_response_to_vacancy):

    response_id = await send_response_to_vacancy()

    status = {
        "status": "hired"
    }

    response = await tenant_client.patch(f"/responses/{response_id}/status", json=status)

    assert response.status_code == 200