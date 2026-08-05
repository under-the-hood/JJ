from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from app.backend.database.database import session_dep
from app.backend.dependencies.user import check_admin, check_user_by_id
from app.backend.models.user import User
from app.backend.schemas.admin import EditUserNameByAdmin, UpdateUserRoleByAdmin
from app.backend.database.redis_database import get_redis
import app.backend.services.admin.users as admin_users


router = APIRouter(prefix="/users", tags=['Admin | Users'])

@router.get('')
async def get_users(session: session_dep, limit: int = 10, offset: int = 0, admin: User = Depends(check_admin)):
    
    users_info = await admin_users.get_users(session=session, limit=limit, offset=offset, admin=admin)
    return {**users_info}


@router.patch('/{user_id}/name')
async def update_name(session: session_dep, data: EditUserNameByAdmin, current_user: User = Depends(check_user_by_id), admin: User = Depends(check_admin), redis: Redis = Depends(get_redis)):

    await admin_users.update_name(session=session, data=data, current_user=current_user, admin=admin, redis=redis)
    return {'success': True, 'message': 'Users name was edited'}


@router.patch('/{user_id}/role')
async def update_role(session: session_dep, data: UpdateUserRoleByAdmin, current_user: User = Depends(check_user_by_id), admin: User = Depends(check_admin), redis: Redis = Depends(get_redis)):

    await admin_users.update_role(session=session, data=data, current_user=current_user, admin=admin, redis=redis)
    return {'success': True, 'message': 'Role was updated'}    


@router.delete('/{user_id}')
async def delete_user(session: session_dep, current_user: User = Depends(check_user_by_id), admin: User = Depends(check_admin), redis: Redis = Depends(get_redis)):

    await admin_users.delete_user(session=session, current_user=current_user, admin=admin, redis=redis)
    return {'success': True, 'message': 'User was deleted'}