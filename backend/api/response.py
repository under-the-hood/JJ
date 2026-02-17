from fastapi import APIRouter, Depends

from backend.database.database import session_dep
from backend.dependencies import check_user, check_vacancy, check_resume
from backend.models.user import User
from backend.models.vacancy import Vacancy
from backend.models.resume import Resume
from backend.schemas.response import ResponseSchema, ResponseRead, SetStatus
from backend.utils.limiter import rate_limiter_factory
from backend.services.response import send_response_to_vacancy, get_responses_to_vacancy, set_status_to_response


router = APIRouter()


response_limiter = rate_limiter_factory("/response/apply_to_vacancy/{vacancy_id}", 5, 60)

@router.post('/response/apply_to_vacancy/{vacancy_id}', tags=['Response'], dependencies=[Depends(response_limiter)])
async def apply_to_vacancy(data: ResponseSchema, session: session_dep, current_vacancy: Vacancy = Depends(check_vacancy), current_resume: Resume = Depends(check_resume), current_user: User = Depends(check_user)):

    response = await send_response_to_vacancy(data, session, current_vacancy, current_resume, current_user)
    return {'success': True, 'message': 'You responded to vacancy', "Response": response}


@router.get('/response/{vacancy_id}/get_responses', response_model=list[ResponseRead], tags=['Response'])
async def get_responses(session: session_dep, current_vacancy: Vacancy = Depends(check_vacancy), current_user: User = Depends(check_user)):

    all_resumes = await get_responses_to_vacancy(session, current_vacancy, current_user)
    return all_resumes


set_status_limiter = rate_limiter_factory("/response/set_status/{response_id}", 5, 60)

@router.put('/response/set_status/{response_id}', tags=['Response'], dependencies=[Depends(set_status_limiter)])
async def set_status(response_id: int, data: SetStatus, session: session_dep, current_user: User = Depends(check_user)):

    await set_status_to_response(response_id, data, session, current_user)
    return {'success': True, 'message': 'Status was updated'}