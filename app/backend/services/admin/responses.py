from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.models.response import Response
from app.backend.models.user import User


async def get_responses(session: AsyncSession, admin: User, limit: int = 10, offset: int = 0):
    
    query = await session.execute(select(Response).limit(limit).offset(offset))    
    responses = query.scalars().all()
    quantity = await session.scalar(select(func.count(Response.id)))

    return {
        'quantity of all responses': quantity,
        'responses': responses
        }


async def delete_response(session: AsyncSession, current_response: Response, admin: User):

    await session.delete(current_response)
    await session.commit()