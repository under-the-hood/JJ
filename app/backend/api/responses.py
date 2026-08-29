from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from app.backend.database.database import session_dep
from app.backend.database.redis_database import get_redis
from app.backend.dependencies.resume import check_applicant
from app.backend.dependencies.vacancy import check_vacancy_owner, check_tenant, check_vacancy, check_tenant_or_admin
from app.backend.dependencies.response import check_response_owner
from app.backend.models.user import User
from app.backend.models.vacancy import Vacancy
from app.backend.models.response import Response
from app.backend.schemas.response import ResponseSchema, ResponseRead, SetStatus, SearchResponses
from app.backend.helpers.rate_limiter import rate_limiter_factory
import app.backend.services.responses as response_service


router = APIRouter(prefix="/responses", tags=["Response"])


response_limiter = rate_limiter_factory("/responses/vacancies/{vacancy_id}", 5, 60)

@router.post('/vacancies/{vacancy_id}', dependencies=[Depends(response_limiter)])
async def send_response_to_vacancy(session: session_dep, data: ResponseSchema, current_vacancy: Vacancy = Depends(check_vacancy), current_user: User = Depends(check_applicant)):

    response = await response_service.send_response_to_vacancy(session=session, data=data, current_vacancy=current_vacancy, current_user=current_user)
    return {'message': 'You responded to vacancy', "response": response}


@router.get("")
async def search_responses(session: session_dep, data: SearchResponses = Depends(), current_user: User = Depends(check_tenant_or_admin)):
    responses, total, source = await response_service.search_responses(session=session, data=data, current_user=current_user)
    return {"responses": responses, "total": total, "source": source}

@router.get('/vacancies/{vacancy_id}', response_model=list[ResponseRead])
async def get_responses(session: session_dep, current_vacancy: Vacancy = Depends(check_vacancy_owner), current_user: User = Depends(check_tenant)):

    responses = await response_service.get_responses(session=session, current_vacancy=current_vacancy, current_user=current_user)
    return responses


set_status_limiter = rate_limiter_factory("/responses/{response_id}/status", 5, 60)

@router.patch('/{response_id}/status', dependencies=[Depends(set_status_limiter)])
async def set_status(session: session_dep, data: SetStatus, current_response: Response = Depends(check_response_owner), current_user: User = Depends(check_tenant)):
    
    await response_service.set_status(session=session, data=data, current_response=current_response, current_user=current_user)
    return {'message': 'Status was updated', "response_id": current_response.id}