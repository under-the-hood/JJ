from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.models.response import Response
from app.backend.models.user import User
from app.backend.helpers.celery_tasks.search import delete_response_task


async def delete_response(session: AsyncSession, current_response: Response, admin: User, redis: Redis):
    delete_response_task.delay(current_response.id)

    await session.delete(current_response)
    await session.commit()