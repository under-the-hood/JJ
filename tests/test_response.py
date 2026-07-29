import pytest
import asyncio


@pytest.mark.asyncio
async def test_send_response_to_vacancy(send_response_to_vacancy, get_latest_emails):
    assert send_response_to_vacancy is not None

    emails = get_latest_emails
    
    assert len(emails) > 0
    assert emails[-1]["subject"] == "New response to your vacancy!"
    assert "city: Almaty" in emails[-1]["text"]


@pytest.mark.asyncio
async def test_get_responses(tenant_client, create_vacancy, send_response_to_vacancy):

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

    response_id = send_response_to_vacancy

    status = {
        "status": "hired"
    }

    response = await tenant_client.put(f"/responses/{response_id}/status", json=status)

    assert response.status_code == 200