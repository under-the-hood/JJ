from datetime import timedelta

import pytest

from app.backend.core.auth import security
from tests.fixtures.users import session_headers


@pytest.mark.asyncio
async def test_logout(tenant_client):
    assert tenant_client.cookies.get("access_token") is not None
    assert tenant_client.cookies.get("csrf_access_token") is not None

    response = await tenant_client.post("/auth/logout")
    assert response.status_code == 200

    assert tenant_client.cookies.get("access_token") is None
    assert tenant_client.cookies.get("csrf_access_token") is None


@pytest.mark.asyncio
async def test_login_with_wrong_password(client):
    login = {
        "email": "applicant_account@example.com",
        "password": "wrong_password"
    }

    response = await client.post("/auth/login", json=login)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_with_nonexistent_email(client):
    login = {
        "email": "nonexistent_email@example.com",
        "password": "12345678"
    }

    response = await client.post("/auth/login", json=login)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout_revokes_token(applicant_client, client):
    headers = session_headers(applicant_client)

    response = await applicant_client.get("/users/me", headers=headers)
    assert response.status_code == 200

    await applicant_client.post("auth/logout")

    response = await client.get("/users/me", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Token has been revoked"


@pytest.mark.asyncio
async def test_logout_twice(applicant_client):
    old_token = {"Cookie": f"token={applicant_client.cookies.get('token')}"}

    first_response = await applicant_client.post("auth/logout")
    assert first_response.status_code == 200

    second_response = await applicant_client.post("auth/logout", headers=old_token)
    assert second_response.status_code == 200


@pytest.mark.asyncio
async def test_logout_with_invalid_token(applicant_client):
    token = {
        "Cookie": "token=garbage"
    }

    response = await applicant_client.post("/auth/logout", headers=token)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_logout_with_expired_token(applicant_client):
    expired = security.create_access_token(uid="1", expiry=timedelta(seconds=-5))
    expired_token = {
        "Cookie": f"token={expired}"
    }

    response = await applicant_client.post("/auth/logout", headers=expired_token)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_logout_blacklist_ttl(applicant_client, get_test_redis):
    token_jti = security._decode_token(applicant_client.cookies.get("access_token")).jti

    await applicant_client.post("/auth/logout")

    ttl = await get_test_redis.ttl(f"blacklist:{token_jti}")
    assert 0 < ttl <= 3600
