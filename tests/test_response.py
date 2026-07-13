import pytest
import asyncio


@pytest.mark.asyncio
async def test_apply_to_vacancy(apply_to_vacancy, get_latest_emails):
    assert apply_to_vacancy is not None

    emails = get_latest_emails
    print(emails)
    
    assert len(emails) > 0
    assert emails[-1]["subject"] == "New response to your vacancy!"
    assert "city: Almaty" in emails[-1]["text"]


@pytest.mark.asyncio
async def test_get_responses(tenant_client, create_vacancy, apply_to_vacancy):

    vacancy_id = create_vacancy

    response = await tenant_client.get(f"/response/{vacancy_id}/get_responses")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0

    first_response = data[0]
    assert "resume" in first_response
    assert "user" in first_response


@pytest.mark.asyncio
async def test_set_status(tenant_client, apply_to_vacancy):

    response_id = apply_to_vacancy

    status = {
        "status": "hired"
    }

    response = await tenant_client.put(f"/response/set_status/{response_id}", json=status)

    assert response.status_code == 200