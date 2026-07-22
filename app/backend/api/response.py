from fastapi import APIRouter, Depends

from app.backend.database.database import session_dep
from app.backend.dependencies.resume import check_applicant
from app.backend.dependencies.vacancy import check_vacancy_owner, check_tenant, check_vacancy
from app.backend.dependencies.response import check_response_owner
from app.backend.models.user import User
from app.backend.models.vacancy import Vacancy
from app.backend.models.response import Response
from app.backend.schemas.response import ResponseSchema, ResponseRead, SetStatus
from app.backend.helpers.rate_limiter import rate_limiter_factory
from app.backend.services.response import send_response_to_vacancy, get_responses_to_vacancy, set_status_to_response


router = APIRouter()


response_limiter = rate_limiter_factory("/response/apply_to_vacancy/{vacancy_id}", 5, 60)

@router.post('/response/apply_to_vacancy/{vacancy_id}', tags=['Response'], dependencies=[Depends(response_limiter)])
async def apply_to_vacancy(session: session_dep, data: ResponseSchema, current_vacancy: Vacancy = Depends(check_vacancy), current_user: User = Depends(check_applicant)):

    response = await send_response_to_vacancy(session=session, data=data, current_vacancy=current_vacancy, current_user=current_user)
    return {'success': True, 'message': 'You responded to vacancy', "Response": response}


@router.get('/response/{vacancy_id}/get_responses', response_model=list[ResponseRead], tags=['Response'])
async def get_responses(session: session_dep, current_vacancy: Vacancy = Depends(check_vacancy_owner), current_user: User = Depends(check_tenant)):

    all_resumes = await get_responses_to_vacancy(session=session, current_vacancy=current_vacancy, current_user=current_user)
    return all_resumes


set_status_limiter = rate_limiter_factory("/response/set_status/{response_id}", 5, 60)

@router.put('/response/set_status/{response_id}', tags=['Response'], dependencies=[Depends(set_status_limiter)])
async def set_status(session: session_dep, data: SetStatus, current_response: Response = Depends(check_response_owner), current_user: User = Depends(check_tenant)):
    
    await set_status_to_response(session=session, data=data, current_response=current_response, current_user=current_user)
    return {'success': True, 'message': 'Status was updated'}