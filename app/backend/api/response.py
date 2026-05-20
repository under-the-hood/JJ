from fastapi import APIRouter, Depends

from app.backend.database.database import session_dep
from app.backend.dependencies.resume import check_resume
from app.backend.dependencies.user import check_user
from app.backend.dependencies.vacancy import check_vacancy
from app.backend.models.user import User
from app.backend.models.vacancy import Vacancy
from app.backend.models.resume import Resume
from app.backend.schemas.response import ResponseSchema, ResponseRead, SetStatus
from app.backend.utils.limiter import rate_limiter_factory
from app.backend.services.response import send_response_to_vacancy, get_responses_to_vacancy, set_status_to_response


router = APIRouter()


response_limiter = rate_limiter_factory("/response/apply_to_vacancy/{vacancy_id}", 5, 60)

@router.post('/response/apply_to_vacancy/{vacancy_id}', tags=['Response'], dependencies=[Depends(response_limiter)])
async def apply_to_vacancy(session: session_dep, data: ResponseSchema, current_vacancy: Vacancy = Depends(check_vacancy), current_resume: Resume = Depends(check_resume), current_user: User = Depends(check_user)):

    response = await send_response_to_vacancy(session, data, current_vacancy, current_resume, current_user)
    return {'success': True, 'message': 'You responded to vacancy', "Response": response}


@router.get('/response/{vacancy_id}/get_responses', response_model=list[ResponseRead], tags=['Response'])
async def get_responses(session: session_dep, current_vacancy: Vacancy = Depends(check_vacancy), current_user: User = Depends(check_user)):

    all_resumes = await get_responses_to_vacancy(session, current_vacancy, current_user)
    return all_resumes


set_status_limiter = rate_limiter_factory("/response/set_status/{response_id}", 5, 60)

@router.put('/response/set_status/{response_id}', tags=['Response'], dependencies=[Depends(set_status_limiter)])
async def set_status(session: session_dep, response_id: int, data: SetStatus, current_user: User = Depends(check_user)):
    
    await set_status_to_response(session, response_id, data, current_user)
    return {'success': True, 'message': 'Status was updated'}