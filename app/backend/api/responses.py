from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from app.backend.database.redis_database import get_redis
from app.backend.database.database import session_dep
from app.backend.dependencies.resume import check_applicant, check_applicant_or_admin
from app.backend.dependencies.vacancy import check_tenant, check_vacancy, check_tenant_or_admin
from app.backend.dependencies.response import check_response_owner_or_admin
from app.backend.models.user import User
from app.backend.models.vacancy import Vacancy
from app.backend.models.response import Response
from app.backend.schemas.response import ResponseSchema,  SetStatus, SearchResponses
from app.backend.helpers.rate_limiter import rate_limiter_factory
import app.backend.services.responses as response_service


router = APIRouter(prefix="/responses", tags=["Response"])

response_limiter = rate_limiter_factory("/responses/vacancies/{vacancy_id}", 5, 60)

@router.post('/vacancies/{vacancy_id}', dependencies=[Depends(response_limiter)])
async def send_response_to_vacancy(session: session_dep, data: ResponseSchema, current_vacancy: Vacancy = Depends(check_vacancy), current_user: User = Depends(check_applicant), redis: Redis = Depends(get_redis)):
    response = await response_service.send_response_to_vacancy(session=session, data=data, current_vacancy=current_vacancy, current_user=current_user, redis=redis)
    return {'message': 'You responded to vacancy', "response": response}


@router.get("")
async def search_responses(session: session_dep, data: SearchResponses = Depends(), current_user: User = Depends(check_tenant_or_admin)):
    responses, total = await response_service.search_responses(session=session, data=data, current_user=current_user)
    return {"responses": responses, "total": total}


@router.get('/my')
async def get_my_responses(session: session_dep, current_user: User = Depends(check_applicant), redis: Redis = Depends(get_redis)):
    responses, total, source = await response_service.get_my_responses(session=session, current_user=current_user, redis=redis)
    return {"responses": responses, "total": total, "source": source}


delete_response_limit = rate_limiter_factory("/responses/{response_id}", 5, 60)

@router.delete("/{response_id}")
async def delete_response(session: session_dep, current_response: Response = Depends(check_response_owner_or_admin), current_user: User = Depends(check_applicant_or_admin), redis: Redis = Depends(get_redis)):
    await response_service.delete_response(session=session, current_response=current_response, current_user=current_user, redis=redis)
    return {"message": "Response was deleted", "response_id": current_response.id}


set_status_limiter = rate_limiter_factory("/responses/{response_id}/status", 5, 60)

@router.patch('/{response_id}/status', dependencies=[Depends(set_status_limiter)])
async def set_status(session: session_dep, data: SetStatus, current_response: Response = Depends(check_response_owner_or_admin), current_user: User = Depends(check_tenant), redis: Redis = Depends(get_redis)):
    await response_service.set_status(session=session, data=data, current_response=current_response, current_user=current_user, redis=redis)
    return {'message': 'Status was updated', "response_id": current_response.id}