import httpx
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import update
import fakeredis.aioredis
import asyncio

from app.main import app
from app.backend.models.base import Base
from app.backend.database.database import engine, get_session
from app.backend.config import settings
from app.backend.core.auth import config
from app.backend.api.response import set_status_limiter, response_limiter
from app.backend.api.user import password_limit, delete_limit, login_limit
from app.backend.api.search import search_vacancy_limiter
from app.backend.database.redis_database import get_redis
from app.backend.helpers.celery import celery
from app.backend.models.user import User


@pytest.fixture(scope='session', autouse=True)
async def setup_db():

    celery.conf.task_always_eager = True
    assert settings.MODE == 'TEST'
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


new_session = async_sessionmaker(autoflush=False, expire_on_commit=False, bind=engine)

@pytest.fixture
async def get_test_session():
    async with new_session() as session:
        app.dependency_overrides[get_session] = lambda: session
        yield session


@pytest.fixture
async def get_latest_emails():
    async with httpx.AsyncClient() as client:
        max_attempts = 5

        for attempt in range(max_attempts):
            try:
                response = await client.get("http://localhost:8080/email")
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        return data
            except httpx.RequestError:
                pass

            if attempt < max_attempts - 1:
                await asyncio.sleep(0.5)

        return []


@pytest.fixture(scope='session', autouse=True)
async def disable_all_limits():
    skip = lambda: None

    limiters = [login_limit, password_limit, delete_limit, set_status_limiter, response_limiter, search_vacancy_limiter]

    for lim in limiters:
        app.dependency_overrides[lim] = skip

    yield


@pytest.fixture(scope="session")
async def test_redis_server():
    return fakeredis.aioredis.FakeServer()


@pytest.fixture(autouse=True)
async def get_test_redis(test_redis_server):

    test_redis_conn = fakeredis.aioredis.FakeRedis(
        server=test_redis_server,
        decode_responses=True)

    app.dependency_overrides[get_redis] = lambda: test_redis_conn

    yield test_redis_conn

    await test_redis_conn.aclose()
    app.dependency_overrides.pop(get_redis, None)


@pytest.fixture
async def admin_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield await get_token(ac, "admin", "admin_account@example.com")

@pytest.fixture
async def applicant_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield await get_token(ac, "applicant", "applicant_account@example.com")

@pytest.fixture
async def tenant_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield await get_token(ac, "tenant", "tenant_account@example.com")


tokens = {
    "tenant_token": None,
    "applicant_token": None,
    "admin_token": None
}

async def get_token(client, role, email):

    token = tokens.get(role)

    reg_role = "tenant" if role == "admin" else role

    new_user = {
        "email": email,
        "name": "artyom",
        "password": "12345678",
        "repeat_password": "12345678",
        "role": reg_role
    }

    if not token:
        login_response = await client.post('/user/sign_in', json={
            'email': email,
            'password': new_user["password"]
        })

        if login_response.status_code != 200:
            await client.post("/user/sign_up", json=new_user)
            
            #Change role in database for admin
            if role == "admin":
                async with new_session() as session:
                    await session.execute(update(User).where(User.email == email).values(role = "admin"))
                    await session.commit()

        login_response = await client.post('/user/sign_in', json={
            'email': email,
            'password': "12345678"
        })

        token = login_response.json().get("token")
        tokens[role] = token

        if not token:
            pytest.fail('No token')

    client.headers.update({"Authorization": f"Bearer {token}"})
    client.cookies.set(config.JWT_ACCESS_COOKIE_NAME, token)

    return client


@pytest.fixture
async def create_vacancy(tenant_client):

    new_vacancy = {
        "title": "Python developer",
        "compensation": 500000,
        "city": "Almaty"
    }

    response = await tenant_client.post("/vacancy/create_vacancy", json=new_vacancy)

    data = response.json()
    assert "Vacancy" in data, data
    vacancy_id = data["Vacancy"]["id"]    

    return vacancy_id

@pytest.fixture
async def create_resume(applicant_client):

    new_resume = {
        "title": "FastAPI Developer",
        "about": "Im a junior FastAPI developer",
        "city": "Almaty",
        "stack": "FastAPI, PostgreSQL, Python"
    }

    response = await applicant_client.post("/resume/create_resume", json=new_resume)

    data = response.json()
    assert "Resume" in data, data
    resume_id = data["Resume"]["id"]

    return resume_id


@pytest.fixture
async def apply_to_vacancy(applicant_client, create_vacancy, create_resume):
        
    query = await applicant_client.get("/user/get_info")
    applicant_id = query.json()["info"]["id"]

    vacancy_id = create_vacancy
    resume_id = create_resume

    cover_letter = {
        "vacancy_id": vacancy_id,
        "resume_id": resume_id,
        "applicant_id": applicant_id,
        "cover_letter": "Hello! I want work in your company!",
        "status": "send"
    }

    response = await applicant_client.post(f"/response/apply_to_vacancy/{vacancy_id}", params={"resume_id": resume_id}, json=cover_letter)

    data = response.json()
    response_id = data["Response"]["id"]

    return response_id