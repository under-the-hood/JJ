from fastapi import APIRouter, Response, Depends
from redis.asyncio import Redis

from backend.database.database import session_dep
from backend.models.user import User
from backend.schemas.user import CreateUser, Login, EditPassword, EditName, Delete
from backend.dependencies import check_user
from backend.utils.limiter import rate_limiter_factory, rate_limiter_factory_by_ip
from backend.database.redis_database import get_redis
from backend.services.user import create_user, login, get_user_info, update_password, update_name, delete_current_user


router = APIRouter()


@router.post('/user/sign_up', tags=['Users'])
async def sign_up(data: CreateUser, session: session_dep):
    
    await create_user(data, session)
    return {'success': True, 'message': 'Account was created'}


login_limit = rate_limiter_factory_by_ip("/user/sign_in", 5, 60)

@router.post('/user/sign_in', tags=['Users'], dependencies=[Depends(login_limit)])
async def sign_in(data: Login, session: session_dep, response: Response):

    logined_user_token = await login(data, session, response)
    return {'success': True, 'message': 'Login succesfull', 'token': logined_user_token}


@router.get('/user/get_info', tags=['Users'])
async def get_info(current_user: User = Depends(check_user), redis: Redis = Depends(get_redis)):

    user_info = await get_user_info(current_user, redis)
    return {**user_info}


password_limit = rate_limiter_factory("/user/edit_password", 5, 60)

@router.put('/user/edit_password', tags=['Users'], dependencies=[Depends(password_limit)])
async def edit_password(data: EditPassword, session: session_dep, current_user: User = Depends(check_user)):

    await update_password(data, session, current_user)
    return {'success': 'True', 'message': 'Password was changed'}


@router.put('/user/edit_name', tags=['Users'])
async def edit_name(data: EditName, session: session_dep, current_user: User = Depends(check_user), redis: Redis = Depends(get_redis)):

    await update_name(data, session, current_user, redis)
    return {'success': True, 'message': 'Name was changed'}


delete_limit = rate_limiter_factory("/user/delete_user", 5, 60)

@router.delete('/user/delete_user', tags=['Users'])
async def delete_user(data: Delete, session: session_dep, current_user = Depends(check_user), redis: Redis = Depends(get_redis)):

    await delete_current_user(data, session, current_user, redis)
    return {'success': True, 'message': 'Account was deleted'}