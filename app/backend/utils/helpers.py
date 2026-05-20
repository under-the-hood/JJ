from fastapi import HTTPException

from app.backend.database.redis_database import Redis
from app.backend.dependencies.redis_cache import get_cache_key
from app.backend.models.user import User, Role


async def clear_user_profile_cache(redis: Redis, user_id: int):
    key = get_cache_key("user", user_id, "profile")
    await redis.delete(key)

def validate_admin_action(current_user: User, current_admin: User):
    if current_user.id == current_admin.id or current_user.role == Role.admin:
        raise HTTPException(status_code=403, detail='You can not edit/delete your/others admin account')

    return current_admin

def validate_user_role(current_user: User, role: Role, error_msg: str):
    if current_user.role != role:
        raise HTTPException(status_code=403, detail=error_msg)