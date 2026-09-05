from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.backend.models.response import Response
from app.backend.models.user import User
from app.backend.helpers.celery_tasks.meilisearch.response import delete_response_task
from app.backend.helpers.cache import clear_user_responses_cache


async def delete_response(session: AsyncSession, current_response: Response, admin: User, redis: Redis):
    await clear_user_responses_cache(redis, current_response.applicant_id)
    delete_response_task.delay(current_response.id)

    await session.delete(current_response)
    await session.commit()