from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from backend.database.database import session_dep
from backend.dependencies import check_user, check_vacancy, check_resume
from backend.models.models import UserModel, VacancyModel, ResumeModel, ResponseModel, Role, ResponseStatus
from backend.schemas.response_schema import ResponseSchema, ResponseReadSchema, SetStatusSchema


router = APIRouter()


@router.post('/response/apply_to_vacancy/{vacancy_id}', tags=['Response'])
async def apply_to_vacancy(data: ResponseSchema, session: session_dep, current_vacancy: VacancyModel = Depends(check_vacancy), current_resume: ResumeModel = Depends(check_resume), current_user: UserModel = Depends(check_user)):

    if current_user.id != current_resume.applicant_id:
        raise HTTPException(status_code=403, detail="It's not your resume")

    if current_user.role != Role.applicant:
        raise HTTPException(status_code=403, detail='Only applicant can apply to vacancy')

    query_check = await session.execute(select(ResponseModel).where(ResponseModel.resume_id == current_resume.id, ResponseModel.vacancy_id == current_vacancy.id))

    if query_check.scalar_one_or_none():
        raise HTTPException(status_code=400, detail='You have already applied to this vacancy with this resume')

    response = ResponseModel(**data.model_dump())

    response.applicant_id = current_user.id
    response.resume_id = current_resume.id
    response.vacancy_id = current_vacancy.id

    session.add(response)
    await session.commit()

    return {'success': True, 'message': 'You responded to vacancy', "Response": response}


@router.get('/response/{vacancy_id}/get_responses', response_model=list[ResponseReadSchema], tags=['Response'])
async def get_responses(session: session_dep, current_vacancy: VacancyModel = Depends(check_vacancy), current_user: UserModel = Depends(check_user)):

    if current_user.role != Role.tenant:
        raise HTTPException(status_code=403, detail='You are not a tenant')

    if current_user.id != current_vacancy.tenant_id:
        raise HTTPException(status_code=403, detail="It's not your vacancy")

    query_responses = await session.execute(
        select(ResponseModel)
        .options(
            joinedload(ResponseModel.resume),
            joinedload(ResponseModel.user)
        )
        .where(ResponseModel.vacancy_id == current_vacancy.id)
    )

    all_resumes = query_responses.scalars().all()

    return all_resumes


@router.put('/response/set_status/{response_id}', tags=['Response'])
async def set_status(response_id: int, data: SetStatusSchema, session: session_dep, current_user: int = Depends(check_user)):

    if current_user.role != Role.tenant:
        raise HTTPException(status_code=403, detail='Only tenatns can set status to responses')

    query_response = await session.execute(select(ResponseModel).options(joinedload(ResponseModel.vacancy)).where(ResponseModel.id == response_id))
    current_response = query_response.scalar_one_or_none()

    if not current_response:
        raise HTTPException(status_code=404, detail='Response not found')

    if current_user.id != current_response.vacancy.tenant_id:
        raise HTTPException(status_code=403, detail="It's not your vacancy")

    current_response.status = data.status

    await session.commit()
    await session.refresh(current_response)

    return {'success': True, 'message': 'Status was updated'}