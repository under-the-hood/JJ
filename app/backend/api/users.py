from fastapi import APIRouter, Response, Depends
from redis.asyncio import Redis

from app.backend.database.database import session_dep
from app.backend.models.user import User
from app.backend.schemas.user import CreateUser, Login, EditPassword, EditName, Delete
from app.backend.dependencies.user import check_user
from app.backend.dependencies.password import validate_user_registration, validate_edit_password, validate_delete_user
from app.backend.helpers.rate_limiter import rate_limiter_factory, rate_limiter_factory_by_ip
from app.backend.database.redis_database import get_redis
import app.backend.services.users as user_service


router = APIRouter(prefix="/users", tags=["Users"])


sign_up_limit = rate_limiter_factory_by_ip("/users/sign_up", 3, 300)

@router.post('/sign_up', dependencies=[Depends(sign_up_limit)])
async def sign_up(session: session_dep, data: CreateUser = Depends(validate_user_registration), redis: Redis = Depends(get_redis)):
    
    user = await user_service.create_user(session=session, data=data, redis=redis)
    return {'message': 'User was created', "user": user}


sign_in_limit = rate_limiter_factory_by_ip("/users/sign_in", 5, 300)

@router.post('/sign_in', dependencies=[Depends(sign_in_limit)])
async def sign_in(session: session_dep, data: Login, response: Response):

    access_token = await user_service.login(session=session, data=data, response=response)
    return {'message': 'Login succesfull', 'token': access_token}


get_info_limit = rate_limiter_factory("/users/me", 30, 60)

@router.get('/me', dependencies=[Depends(get_info_limit)])
async def get_info(current_user: User = Depends(check_user), redis: Redis = Depends(get_redis)):

    info, source = await user_service.get_info(current_user=current_user, redis=redis)
    return {"info": info, "source": source}


password_limit = rate_limiter_factory("/users/me/password", 3, 300)

@router.patch('/me/password', dependencies=[Depends(password_limit)])
async def update_password(session: session_dep, data: EditPassword = Depends(validate_edit_password), current_user: User = Depends(check_user), redis: Redis = Depends(get_redis)):

    await user_service.update_password(session=session, data=data, current_user=current_user, redis=redis)
    return {'message': 'Password was changed'}


@router.patch('/me/name')
async def update_name(session: session_dep, data: EditName, current_user: User = Depends(check_user), redis: Redis = Depends(get_redis)):

    await user_service.update_name(session=session, data=data, current_user=current_user, redis=redis)
    return {'message': 'Name was changed', "user": current_user}


@router.delete('/me')
async def delete_user(session: session_dep, data: Delete = Depends(validate_delete_user), current_user: User = Depends(check_user), redis: Redis = Depends(get_redis)):

    await user_service.delete_user(session=session, data=data, current_user=current_user, redis=redis)
    return {'message': 'Account was deleted', "user_id": current_user.id}