from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from app.backend.database.database import session_dep
from app.backend.dependencies.user import check_admin, check_user_by_id
from app.backend.models.user import User
from app.backend.schemas.admin import UpdateUser
from app.backend.database.redis_database import get_redis
import app.backend.services.admin.users as admin_users
from app.backend.schemas.user import SearchUsers


router = APIRouter(prefix="/users", tags=['Admin | Users'])

@router.get("")
async def search_users(data: SearchUsers = Depends(), admin: User = Depends(check_admin), redis: Redis = Depends(get_redis)):
    users, total, source = await admin_users.search_users(data=data, admin=admin, redis=redis)
    return {"users": users, "total": total, "source": source}


@router.patch("/{user_id}")
async def update_user(session: session_dep, data: UpdateUser, current_user: User = Depends(check_user_by_id), admin: User = Depends(check_admin), redis: Redis = Depends(get_redis)):
    await admin_users.update_user(session=session, data=data, current_user=current_user, admin=admin, redis = redis)
    return {"message": "User was updated", "user": current_user}


@router.delete('/{user_id}')
async def delete_user(session: session_dep, current_user: User = Depends(check_user_by_id), admin: User = Depends(check_admin), redis: Redis = Depends(get_redis)):
    await admin_users.delete_user(session=session, current_user=current_user, admin=admin, redis=redis)
    return {'message': 'User was deleted', "user_id": current_user.id}