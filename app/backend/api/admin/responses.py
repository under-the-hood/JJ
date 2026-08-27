from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from app.backend.database.database import session_dep
from app.backend.dependencies.user import check_admin
from app.backend.dependencies.response import check_response
from app.backend.models.user import User
from app.backend.models.response import Response
import app.backend.services.admin.responses as admin_responses
from app.backend.database.redis_database import get_redis


router = APIRouter(prefix="/responses", tags=['Admin | Responses'])

@router.delete('/{response_id}')
async def delete_response(session: session_dep, current_response: Response = Depends(check_response), admin: User = Depends(check_admin), redis: Redis = Depends(get_redis)):

    await admin_responses.delete_response(session=session, current_response=current_response, admin=admin, redis=redis)
    return {'message': 'Response was deleted', "response_id": current_response.id}