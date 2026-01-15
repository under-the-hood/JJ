import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import async_sessionmaker

from main import app
from backend.database.database import Base, engine, get_session
from backend.database.config import settings


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

@pytest.fixture
async def ac():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client