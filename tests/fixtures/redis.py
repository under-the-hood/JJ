import pytest
import fakeredis.aioredis

from app.main import app
from app.backend.database.redis_database import get_redis


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