import pytest


@pytest.mark.order(-1)
async def test_limiter_on_search_resumes(get_token_as_tenant):
    status_codes = []

    for i in range(7):
        response = await get_token_as_tenant.get("/search/search_resumes")
        status_codes.append(response.status_code)

    assert status_codes[0] == 200
    assert status_codes[-1] == 429