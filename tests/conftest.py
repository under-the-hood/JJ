import httpx
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import update
import fakeredis.aioredis

from app.main import app
from app.backend.models.base import Base
from app.backend.database.database import engine, get_session
from app.backend.config import settings
from app.backend.api.responses import set_status_limiter, response_limiter
from app.backend.api.users import password_limit, sign_in_limit, sign_up_limit
from app.backend.api.search import search_vacancy_limiter
from app.backend.api.resumes import create_resume_limit
from app.backend.api.vacancies import create_vacancy_limit
from app.backend.database.redis_database import get_redis
from app.backend.helpers.celery import celery
from app.backend.models.user import User


@pytest.fixture(scope='session', autouse=True)
async def setup_db():

    celery.conf.update(task_always_eager=True, task_eager_propagates=True)
    assert settings.MODE == 'TEST'
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(autouse=True)
async def get_test_session():
    async with engine.connect() as conn:
        transaction = await conn.begin()
        async_session = async_sessionmaker(autoflush=False, expire_on_commit=False, bind=conn)
        
        async with async_session() as session:
            app.dependency_overrides[get_session] = lambda: session
            yield session

        await transaction.rollback()

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def mock_celery(mocker):
    return mocker.patch("app.backend.helpers.celery_tasks.send_mail_task.delay")


@pytest.fixture(scope='session', autouse=True)
async def disable_all_limits():
    skip = lambda: None

    limiters = [
        sign_up_limit,
        sign_in_limit, 
        password_limit, 
        set_status_limiter, 
        response_limiter, 
        search_vacancy_limiter, 
        create_vacancy_limit, 
        create_resume_limit
        ]

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

    await test_redis_conn.flushall()
    await test_redis_conn.aclose()
    app.dependency_overrides.pop(get_redis, None)


async def get_token(client, role, email, session):
    reg_role = "tenant" if role == "admin" else role

    new_user = {
        "email": email,
        "name": "artyom",
        "password": "12345678",
        "repeat_password": "12345678",
        "role": reg_role
    }

    await client.post("/users/sign_up", json=new_user)
            
    #Change role in database for admin
    if role == "admin":
        await session.execute(update(User).where(User.email == email).values(role = "admin"))
        await session.flush()

    login_response = await client.post('/users/sign_in', json={
        'email': email,
        'password': new_user["password"]
    })

    return login_response.json().get("token")


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
async def admin_client(client, get_test_session):
    return await create_client(client, "admin", "admin_account@example.com", get_test_session)

@pytest.fixture
async def applicant_client(client, get_test_session):
    return await create_client(client, "applicant", "applicant_account@example.com", get_test_session)

@pytest.fixture
async def tenant_client(client, get_test_session):
    return await create_client(client, "tenant", "tenant_account@example.com", get_test_session)


@pytest.fixture
async def create_vacancy(tenant_client):

    new_vacancy = {
        "title": "Python developer",
        "compensation": 500000,
        "city": "Almaty"
    }

    response = await tenant_client.post("/vacancies", json=new_vacancy)

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

    response = await applicant_client.post("/resumes", json=new_resume)

    data = response.json()
    assert "Resume" in data, data
    resume_id = data["Resume"]["id"]

    return resume_id


@pytest.fixture
def send_response_to_vacancy(applicant_client, create_vacancy, create_resume):
    async def create_response():
        cover_letter = {
            "resume_id": create_resume,
            "cover_letter": "Hello! I want work in your company!",
        }

        response = await applicant_client.post(f"/responses/vacancies/{create_vacancy}", params={"resume_id": create_resume}, json=cover_letter)

        data = response.json()
        response_id = data["Response"]["id"]

        return response_id
    return create_response