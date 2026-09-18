import pytest


@pytest.mark.asyncio
async def test_create_vacancy(create_vacancy):
    assert create_vacancy is not None


@pytest.mark.asyncio
async def test_my_vacancies(tenant_client, create_vacancy):
    response = await tenant_client.get("/vacancies/my")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data["vacancies"], list)
    assert len(data["vacancies"]) > 0
    assert data["vacancies"][0]["title"] == "Python developer"


@pytest.mark.asyncio
async def test_update_vacancy(tenant_client, create_vacancy):
    vacancy_id = create_vacancy

    updated_vacancy = {
        "new_title": "FastAPI Developer",
        "new_compensation": 550000,
        "new_city": "Astana"
    }

    response = await tenant_client.patch(f"/vacancies/{vacancy_id}", json=updated_vacancy)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_vacancy(tenant_client, create_vacancy):
    vacancy_id = create_vacancy

    response = await tenant_client.request("DELETE", f"/vacancies/{vacancy_id}")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_vacancy_as_applicant(applicant_client, valid_vacancy_payload):
    response = await applicant_client.post("/vacancies", json=valid_vacancy_payload)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_vacancy_without_auth(client, valid_vacancy_payload):
    response = await client.post("/vacancies", json=valid_vacancy_payload)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_vacancy_with_negative_compensation(tenant_client, valid_vacancy_payload):
    vacancy = {**valid_vacancy_payload, "compensation": -100000}

    response = await tenant_client.post("/vacancies", json=vacancy)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_vacancy_with_too_short_title(tenant_client, valid_vacancy_payload):
    vacancy = {**valid_vacancy_payload, "title": "Py"}

    response = await tenant_client.post("/vacancies", json=vacancy)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_vacancy_with_invalid_city(tenant_client, valid_vacancy_payload):
    vacancy = {**valid_vacancy_payload, "city": "<Almaty>"}

    response = await tenant_client.post("/vacancies", json=vacancy)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_nonexistent_vacancy(tenant_client, valid_vacancy_payload):
    vacancy_id = 99999

    response = await tenant_client.patch(f"/vacancies/{vacancy_id}", json=valid_vacancy_payload)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_nonexistent_vacancy(tenant_client):
    vacancy_id = 99999

    response = await tenant_client.request("DELETE", f"/vacancies/{vacancy_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_vacancy_as_not_owner(create_vacancy, second_tenant_client, valid_vacancy_payload):
    response = await second_tenant_client.patch(f"/vacancies/{create_vacancy}", json=valid_vacancy_payload)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_vacancy_as_not_owner(create_vacancy, second_tenant_client):
    response = await second_tenant_client.request("DELETE", f"/vacancies/{create_vacancy}")
    assert response.status_code == 403
