import pytest


@pytest.mark.anyio
async def test_user_info_cache_invalidation(get_token_as_tenant):

    await get_token_as_tenant.get("/user/get_info")
    first_response = await get_token_as_tenant.get("/user/get_info")

    data = first_response.json()
    assert data["source"] == "cache"

    new_name = {
        "password": "12345678",
        "new_name": "Anton"
    }

    await get_token_as_tenant.put("/user/edit_name", json=new_name)

    second_response = await get_token_as_tenant.get("/user/get_info")
    
    data = second_response.json()
    assert data["source"] == "db"


@pytest.mark.anyio
async def test_vacancy_search_invalidation(get_token_as_applicant, get_token_as_tenant):

    first_response = await get_token_as_applicant.get("/search/search_vacancies")
    assert first_response.json()["source"] == "db"

    second_response = await get_token_as_applicant.get("/search/search_vacancies")
    assert second_response.json()["source"] == "cache"

    new_vacancy = {
        "title": "Senior Python Developer",
        "city": "Almaty",
        "compensation": 500000
    }

    await get_token_as_tenant.post("/vacancy/create_vacancy", json=new_vacancy)

    third_response = await get_token_as_applicant.get("/search/search_vacancies")
    assert third_response.json()["source"] == "db"

    titles = [v["title"] for v in third_response.json()["vacancies"]]
    assert "Senior Python Developer" in titles