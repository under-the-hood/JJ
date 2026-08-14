import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.main import app
from app.backend.models.base import Base
from app.backend.database.database import engine, get_session
from app.backend.config import settings
from app.backend.helpers.celery import celery


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
async def test_session():
    async with engine.connect() as conn:
        transaction = await conn.begin()
        async_session = async_sessionmaker(autoflush=False, expire_on_commit=False, bind=conn, join_transaction_mode="create_savepoint")
        
        async with async_session() as session:
            app.dependency_overrides[get_session] = lambda: session
            yield session

        await transaction.rollback()

    app.dependency_overrides.pop(get_session, None)