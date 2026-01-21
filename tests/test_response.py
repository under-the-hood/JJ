import pytest


@pytest.mark.anyio
async def test_apply_to_vacancy(apply_to_vacancy):
    assert apply_to_vacancy is not None


@pytest.mark.anyio
async def test_get_responses(get_token_as_tenant, create_vacancy, apply_to_vacancy):

    vacancy_id = create_vacancy

    response = await get_token_as_tenant.get(f"/response/{vacancy_id}/get_responses")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0

    first_response = data[0]
    assert "resume" in first_response
    assert "user" in first_response


@pytest.mark.anyio
async def test_set_status(get_token_as_tenant, apply_to_vacancy):

    response_id = apply_to_vacancy

    status = {
        "status": "hired"
    }

    response = await get_token_as_tenant.put(f"/response/set_status/{response_id}", json=status)

    assert response.status_code == 200