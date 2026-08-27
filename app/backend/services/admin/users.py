from redis.asyncio import Redis
import json
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.models.user import User
from app.backend.schemas.admin import UpdateUser
from app.backend.helpers.cache import clear_user_profile_cache
from app.backend.helpers.validator import validate_admin_action
from app.backend.schemas.user import SearchUsers
from app.backend.utils.search import meili
from app.backend.helpers.celery_tasks.search import sync_user_task, delete_user_task


async def search_users(data: SearchUsers, admin: User, redis: Redis):
    version = await redis.get("user_version") or "0"
    search_params = f"version:{version}_q:{data.email or ''}_name:{data.name or ''}_limit:{data.limit}_offset:{data.offset}"
    cache_key = f"search:users:{search_params}"

    cached_users = await redis.get(cache_key)
    if cached_users:
        users = json.loads(cached_users)
        return users, len(users), "cache"

    search_options = {
        "limit": data.limit,
        "offset": data.offset
    }

    query_parts = []
    if data.email:
        query_parts.append(data.email.strip())

    if data.name:
        query_parts.append(data.name.strip())

    query_text = " ".join(query_parts)

    result = meili.index("users").search(query_text, search_options)
    users = result["hits"]

    total = result.get("estimatedTotalHits", len(users))
    await redis.set(cache_key, json.dumps(users), ex=300)

    return users, total, "db"


async def update_user(session: AsyncSession, data: UpdateUser, current_user: User, admin: User, redis: Redis):
    validate_admin_action(current_user, admin)

    if data.new_name:
        current_user.name = data.new_name
    
    if data.new_role:
        current_user.role = data.new_role

    await session.commit()
    await session.refresh(current_user)

    sync_user_task.delay(current_user.id)
    await redis.incr("user_version")
    await clear_user_profile_cache(redis, current_user.id)


async def delete_user(session: AsyncSession, current_user: User, admin: User, redis: Redis):
    validate_admin_action(current_user, admin)

    await session.delete(current_user)
    await session.commit()

    delete_user_task.delay(current_user.id)
    await redis.incr("user_version")
    await clear_user_profile_cache(redis, current_user.id)