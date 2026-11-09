from authx import TokenPayload
from fastapi import APIRouter, Cookie, Depends, Header, Response
from redis.asyncio import Redis

import app.backend.services.auth as auth_service
from app.backend.core.auth import security
from app.backend.database.database import session_dep
from app.backend.database.redis_database import get_redis
from app.backend.helpers.rate_limiter import (
    rate_limiter_factory_by_ip,
)
from app.backend.schemas.user import Login

router = APIRouter(prefix="/auth", tags=["Auth"])


login_limit = rate_limiter_factory_by_ip("/auth/login", 5, 300)

@router.post('/login', dependencies=[Depends(login_limit)])
async def login(session: session_dep, data: Login, response: Response):
    access_token, refresh_token = await auth_service.login(session=session, data=data, response=response)
    return {'message': 'Login succesfull', 'access token': access_token, "refresh token": refresh_token}


@router.post("/refresh")
async def refresh(response: Response, payload: TokenPayload = Depends(security.refresh_token_required), x_csrf_token: str | None = Header(default=None, alias="X-CSRF-TOKEN"), redis: Redis = Depends(get_redis)):
    access_token = await auth_service.refresh(response=response, payload=payload, redis=redis)
    return {"access token": access_token}


@router.post("/logout")
async def logout(response: Response, access_token: str = Cookie(default=None), refresh_token: str = Cookie(default=None), redis: Redis = Depends(get_redis)):
    await auth_service.logout(response=response, access_token=access_token, refresh_token=refresh_token, redis=redis)
    return {"message": "logged out"}
