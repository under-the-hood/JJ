from sqlalchemy import select, func
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.models.user import User
from app.backend.schemas.admin import UpdateUser
from app.backend.helpers.cache import clear_user_profile_cache
from app.backend.helpers.validator import validate_admin_action


async def get_users(session: AsyncSession, admin: User, limit: int = 10, offset: int = 0):
    query = await session.execute(select(User).limit(limit).offset(offset))
    users = query.scalars().all()

    total = await session.scalar(select(func.count(User.id)))

    return total, users


async def update_user(session: AsyncSession, data: UpdateUser, current_user: User, admin: User, redis: Redis):
    validate_admin_action(current_user, admin)

    if data.new_name:
        current_user.name = data.new_name
    
    if data.new_role:
        current_user.role = data.new_role

    await session.commit()
    await session.refresh(current_user)

    await clear_user_profile_cache(redis, current_user.id)


async def delete_user(session: AsyncSession, current_user: User, admin: User, redis: Redis):
    validate_admin_action(current_user, admin)

    await session.delete(current_user)
    await session.commit()

    await clear_user_profile_cache(redis, current_user.id)