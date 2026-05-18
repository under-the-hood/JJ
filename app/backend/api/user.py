from fastapi import APIRouter, Response, Depends
from redis.asyncio import Redis

from app.backend.database.database import session_dep
from app.backend.models.user import User
from app.backend.schemas.user import CreateUser, Login, EditPassword, EditName, Delete
from app.backend.dependencies.user import check_user
from app.backend.dependencies.password import validate_user_registration, verify_password, validate_new_password
from app.backend.utils.limiter import rate_limiter_factory, rate_limiter_factory_by_ip
from app.backend.database.redis_database import get_redis
from app.backend.services.user import create_user, login, get_user_info, update_password, update_name, delete_current_user


router = APIRouter()


@router.post('/user/sign_up', tags=['Users'])
async def sign_up(session: session_dep, data: CreateUser = Depends(validate_user_registration)):
    
    await create_user(session, data)
    return {'success': True, 'message': 'Account was created'}


login_limit = rate_limiter_factory_by_ip("/user/sign_in", 5, 60)

@router.post('/user/sign_in', tags=['Users'], dependencies=[Depends(login_limit)])
async def sign_in(session: session_dep, data: Login, response: Response):

    access_token = await login(session, data, response)
    return {'success': True, 'message': 'Login succesfull', 'token': access_token}


@router.get('/user/get_info', tags=['Users'])
async def get_info(current_user: User = Depends(check_user), redis: Redis = Depends(get_redis)):

    user_info = await get_user_info(current_user, redis)
    return {**user_info}


password_limit = rate_limiter_factory("/user/edit_password", 5, 60)

@router.put('/user/edit_password', tags=['Users'], dependencies=[Depends(password_limit)])
async def edit_password(session: session_dep, data: EditPassword = Depends(validate_new_password), current_user: User = Depends(check_user), redis: Redis = Depends(get_redis)):

    await update_password(session, data, current_user, redis)
    return {'success': True, 'message': 'Password was changed'}


@router.put('/user/edit_name', tags=['Users'])
async def edit_name(session: session_dep, data: EditName, current_user: User = Depends(check_user), redis: Redis = Depends(get_redis)):

    await update_name(session, data, current_user, redis)
    return {'success': True, 'message': 'Name was changed'}


delete_limit = rate_limiter_factory("/user/delete_user", 5, 60)

@router.delete('/user/delete_user', tags=['Users'])
async def delete_user(session: session_dep, data: Delete = Depends(verify_password), current_user: User = Depends(check_user), redis: Redis = Depends(get_redis)):

    await delete_current_user(session, data, current_user, redis)
    return {'success': True, 'message': 'Account was deleted'}