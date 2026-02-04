import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import text
from redis.asyncio import Redis

from main import app
from backend.database.database import Base, engine, get_session
from backend.database.config import settings
from backend.database.hash import config
from backend.api.response_api import set_status_limiter, response_limiter
from backend.api.user_api import password_limit, delete_limit, login_limit
from backend.api.search_api import search_vacancy_limiter


@pytest.fixture(scope='session', autouse=True)
async def setup_db():
    print(f'{settings.database=}')
    
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

        app.dependency_overrides.clear()


@pytest.fixture(scope='session', autouse=True)
async def disable_all_limits():
    skip = lambda: None

    limiters = [login_limit, password_limit, delete_limit, set_status_limiter, response_limiter, search_vacancy_limiter]

    for lim in limiters:
        app.dependency_overrides[lim] = skip

    yield

    app.dependency_overrides.clear() 


@pytest.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest.fixture
async def client_applicant():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield await get_token(ac, "applicant", "applicant_account@example.com")

@pytest.fixture
async def client_tenant():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
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
                    await session.execute(text("UPDATE users SET role = 'admin' WHERE email = 'admin_account@example.com'"))
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
async def get_token_as_tenant(client_tenant):

    new_user = await get_token(
        client=client_tenant,
        email="tenant_account@example.com",
        role="tenant"
    )

    return new_user


@pytest.fixture
async def get_token_as_applicant(client_applicant):

    new_user = await get_token(
        client=client_applicant,
        email="applicant_account@example.com",
        role="applicant"
    )

    return new_user

@pytest.fixture
async def get_token_as_admin(async_client):

    new_user = await get_token(
        client=async_client,
        email="admin_account@example.com",
        role="admin"
    )

    return new_user


@pytest.fixture
async def create_vacancy(get_token_as_tenant):

    new_vacancy = {
        "title": "Python developer",
        "compensation": 500000,
        "city": "Almaty"
    }

    response = await get_token_as_tenant.post("/vacancy/create_vacancy", json=new_vacancy)

    data = response.json()
    assert "Vacancy" in data, data
    vacancy_id = data["Vacancy"]["id"]    

    return vacancy_id


@pytest.fixture
async def create_resume(get_token_as_applicant):

    new_resume = {
        "title": "FastAPI Developer",
        "about": "Im a junior FastAPI developer",
        "city": "Almaty",
        "stack": "FastAPI, PostgreSQL, Python"
    }

    response = await get_token_as_applicant.post("/resume/create_resume", json=new_resume)

    data = response.json()
    assert "Resume" in data, data
    resume_id = data["Resume"]["id"]

    return resume_id


@pytest.fixture
async def apply_to_vacancy(get_token_as_applicant, create_vacancy, create_resume):
        
    query = await get_token_as_applicant.get("/user/get_info")
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

    response = await get_token_as_applicant.post(f"/response/apply_to_vacancy/{vacancy_id}", params={"resume_id": resume_id}, json=cover_letter)

    data = response.json()
    response_id = data["Response"]["id"]

    return response_id