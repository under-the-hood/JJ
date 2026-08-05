from sqlalchemy import select, func
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.models.user import User
from app.backend.schemas.admin import EditUserNameByAdmin, UpdateUserRoleByAdmin
from app.backend.dependencies.redis_cache import get_cache_key
from app.backend.helpers.cache import clear_user_profile_cache
from app.backend.helpers.validator import validate_admin_action


async def get_users(session: AsyncSession, admin: User, limit: int = 10, offset: int = 0):
    query = await session.execute(select(User).limit(limit).offset(offset))
    users = query.scalars().all()

    quantity = await session.scalar(select(func.count(User.id)))

    return {
        'quantity of all users': quantity,
        'users': users
    }


async def update_name(session: AsyncSession, data: EditUserNameByAdmin, current_user: User, admin: User, redis: Redis):
    validate_admin_action(current_user, admin)

    current_user.name = data.new_name

    await session.commit()
    await session.refresh(current_user)

    key = get_cache_key("user", current_user.id, "profile")
    await redis.delete(key)


async def update_role(session: AsyncSession, data: UpdateUserRoleByAdmin, current_user: User, admin: User, redis: Redis):
    validate_admin_action(current_user, admin)

    current_user.role = data.new_role

    await session.commit()
    await session.refresh(current_user)

    await clear_user_profile_cache(redis, current_user.id)


async def delete_user(session: AsyncSession, current_user: User, admin: User, redis: Redis):
    validate_admin_action(current_user, admin)

    await session.delete(current_user)
    await session.commit()

    await clear_user_profile_cache(redis, current_user.id)