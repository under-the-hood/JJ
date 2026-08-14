import pytest
from contextlib import asynccontextmanager
from httpx import AsyncClient, ASGITransport

from app.main import app
from tests.fixtures.auth import get_token


@asynccontextmanager
async def create_client(role: str, email: str, session):
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Получаем токен для конкретной роли и email
        token = await get_token(ac, role, email, session)
        
        # 2. Устанавливаем Bearer token в дефолтные заголовки клиента
        ac.headers["Authorization"] = f"Bearer {token}"
        
        yield ac


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def admin_client(test_session):
    async with create_client("admin", "admin_account@example.com", test_session) as ac:
        yield ac


@pytest.fixture
async def applicant_client(test_session):
    async with create_client("applicant", "applicant_account@example.com", test_session) as ac:
        yield ac


@pytest.fixture
async def tenant_client(test_session):
    async with create_client("tenant", "tenant_account@example.com", test_session) as ac:
        yield ac