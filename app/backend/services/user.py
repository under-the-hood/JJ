from fastapi import HTTPException, Response
from sqlalchemy import select
from redis.asyncio import Redis
import json
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.utils.hash import hashing_password, pwd_context
from app.backend.core.auth import security
from app.backend.models.user import User
from app.backend.schemas.user import CreateUser, Login, EditPassword, EditName, Delete
from app.backend.dependencies.redis_cache import get_cache_key
from app.backend.models.mails import Mails
from app.backend.helpers.celery_tasks import send_mail_task
from app.backend.helpers.cache import clear_user_profile_cache


async def create_user(session: AsyncSession, data: CreateUser):

    new_user = User(
        email = data.email,
        role = data.role,
        name = data.name,
        password = hashing_password(data.password)
    )

    if data.role == "tenant":
        message_body = f"Hello, {data.name}!\n Thank you for joining us. Now you can find the best candidates for your vacancies. Start by creating your first vacancy!"
    else:
        message_body = f"Hello, {data.name}!\n Thank you for joining us. Now you can find your dream job. Start by creating your resume!"

    session.add(new_user)
    await session.flush()

    mail = Mails(
        recipient_id = new_user.id,
        subject = "Welcome to JJ!",
        body = message_body
    )

    session.add(mail)
    await session.commit()
    send_mail_task.delay(mail.id)

    return new_user


async def login(session: AsyncSession, data: Login, response: Response):

    query = await session.execute(select(User).where(User.email == data.email))
    current_user = query.scalar_one_or_none()

    if not current_user or not pwd_context.verify(data.password, current_user.password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    token = security.create_access_token(uid=str(current_user.id))
    security.set_access_cookies(token, response=response)

    return token


async def get_user_info(current_user: User, redis: Redis):

    key = get_cache_key("user", current_user.id, "profile")
    cached_info = await redis.get(key)

    #If info about user have in redis, return cached info
    if cached_info:
        return {"success": True, "info": json.loads(cached_info), "source": "cache"}

    user_info = {'id': current_user.id,
                    'email': current_user.email,
                    'name': current_user.name,
                    'role': str(current_user.role)}
    
    #Else save info about user in cache on 1 hour
    await redis.set(key, json.dumps(user_info), ex=3600)

    return {"success": True, "info": user_info, "source": "db"}


async def update_password(session: AsyncSession, data: EditPassword, current_user: User, redis: Redis):

    current_user.password = hashing_password(data.new_password)

    mail = Mails(
        recipient_id = current_user.id,
        subject = "Your password has been changed",
        body = f"Hello {current_user.name}!\nThis is a confirmation that the password for your account was recently changed. If you did not make this change, please contact our support team immediately to secure your account."
    )

    session.add(mail)
    await session.commit()
    await session.refresh(current_user)
    send_mail_task.delay(mail.id)

    await clear_user_profile_cache(redis, current_user.id)


async def update_name(session: AsyncSession, data: EditName, current_user: User, redis: Redis):

    current_user.name = data.new_name

    await session.commit()
    await session.refresh(current_user)

    #Delete cache
    await clear_user_profile_cache(redis, current_user.id)


async def delete_current_user(session: AsyncSession, data: Delete, current_user: User, redis: Redis):

    await session.delete(current_user)
    await session.commit()

    await clear_user_profile_cache(redis, current_user.id)