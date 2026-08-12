import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from tests.fixtures.auth import get_token


async def create_client(client, role, email, session):
    transport = ASGITransport(app=app)
    ac = AsyncClient(transport=transport, base_url="http://test")

    token = await get_token(ac, role, email, session)
    ac.headers["Authorization"] = f"Bearer {token}"
    return ac


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def admin_client(client, test_session):
    return await create_client(client, "admin", "admin_account@example.com", test_session)

@pytest.fixture
async def applicant_client(client, test_session):
    return await create_client(client, "applicant", "applicant_account@example.com", test_session)

@pytest.fixture
async def tenant_client(client, test_session):
    return await create_client(client, "tenant", "tenant_account@example.com", test_session)