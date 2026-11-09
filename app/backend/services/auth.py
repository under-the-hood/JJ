from authx import TokenPayload
from fastapi import Cookie, HTTPException, Response
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.core.auth import security
from app.backend.helpers.auth import revoke_token
from app.backend.models.user import User
from app.backend.schemas.user import Login
from app.backend.utils.hash import pwd_context


async def login(session: AsyncSession, data: Login, response: Response):
    query = await session.execute(select(User).where(User.email == data.email))
    current_user = query.scalar_one_or_none()

    if not current_user or not pwd_context.verify(data.password, current_user.password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access_token = security.create_access_token(uid=str(current_user.id))
    refresh_token = security.create_refresh_token(uid=str(current_user.id))

    security.set_access_cookies(access_token, response=response)
    security.set_refresh_cookies(refresh_token, response=response)

    return access_token, refresh_token


async def refresh(response: Response, payload: TokenPayload, redis: Redis):
    if await redis.exists(f"blacklist:{payload.jti}"):
        raise HTTPException(status_code=401, detail="Token has been revoked")

    access_token = security.create_access_token(uid=payload.sub)
    security.set_access_cookies(access_token, response=response)

    return access_token


async def logout(response: Response, access_token: Cookie, refresh_token: Cookie, redis: Redis):
    await revoke_token(access_token, redis)
    await revoke_token(refresh_token, redis)

    security.unset_cookies(response=response)
    if security.config.JWT_COOKIE_CSRF_PROTECT:
        response.delete_cookie("csrf_access_token")
        response.delete_cookie("csrf_refresh_token")
