from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from backend.database.database import session_dep
from backend.dependencies import check_user, check_vacancy, check_resume
from backend.models.response import Response
from backend.models.user import User, Role
from backend.models.vacancy import Vacancy
from backend.models.resume import Resume
from backend.schemas.response import ResponseSchema, ResponseRead, SetStatus
from backend.utils.limiter import rate_limiter_factory


router = APIRouter()


response_limiter = rate_limiter_factory("/response/apply_to_vacancy/{vacancy_id}", 5, 60)

@router.post('/response/apply_to_vacancy/{vacancy_id}', tags=['Response'], dependencies=[Depends(response_limiter)])
async def apply_to_vacancy(data: ResponseSchema, session: session_dep, current_vacancy: Vacancy = Depends(check_vacancy), current_resume: Resume = Depends(check_resume), current_user: User = Depends(check_user)):

    if current_user.id != current_resume.applicant_id:
        raise HTTPException(status_code=403, detail="It's not your resume")

    if current_user.role != Role.applicant:
        raise HTTPException(status_code=403, detail='Only applicant can apply to vacancy')

    query_check = await session.execute(select(Response).where(Response.resume_id == current_resume.id, Response.vacancy_id == current_vacancy.id))

    if query_check.scalar_one_or_none():
        raise HTTPException(status_code=400, detail='You have already applied to this vacancy with this resume')

    response = Response(**data.model_dump())

    response.applicant_id = current_user.id
    response.resume_id = current_resume.id
    response.vacancy_id = current_vacancy.id

    session.add(response)
    await session.commit()

    return {'success': True, 'message': 'You responded to vacancy', "Response": response}


@router.get('/response/{vacancy_id}/get_responses', response_model=list[ResponseRead], tags=['Response'])
async def get_responses(session: session_dep, current_vacancy: Vacancy = Depends(check_vacancy), current_user: User = Depends(check_user)):

    if current_user.role != Role.tenant:
        raise HTTPException(status_code=403, detail='You are not a tenant')

    if current_user.id != current_vacancy.tenant_id:
        raise HTTPException(status_code=403, detail="It's not your vacancy")

    query_responses = await session.execute(
        select(Response)
        .options(
            joinedload(Response.resume),
            joinedload(Response.user)
        )
        .where(Response.vacancy_id == current_vacancy.id)
    )

    all_resumes = query_responses.scalars().all()

    return all_resumes


set_status_limiter = rate_limiter_factory("/response/set_status/{response_id}", 5, 60)

@router.put('/response/set_status/{response_id}', tags=['Response'], dependencies=[Depends(set_status_limiter)])
async def set_status(response_id: int, data: SetStatus, session: session_dep, current_user: int = Depends(check_user)):

    if current_user.role != Role.tenant:
        raise HTTPException(status_code=403, detail='Only tenatns can set status to responses')

    query_response = await session.execute(select(Response).options(joinedload(Response.vacancy)).where(Response.id == response_id))
    current_response = query_response.scalar_one_or_none()

    if not current_response:
        raise HTTPException(status_code=404, detail='Response not found')

    if current_user.id != current_response.vacancy.tenant_id:
        raise HTTPException(status_code=403, detail="It's not your vacancy")

    current_response.status = data.status

    await session.commit()
    await session.refresh(current_response)

    return {'success': True, 'message': 'Status was updated'}