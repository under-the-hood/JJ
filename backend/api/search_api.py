from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from pydantic import Field

from backend.dependencies import get_user_token
from backend.database.database import session_dep
from backend.models.models import ResumeModel, UserModel, Role, VacancyModel
from backend.schemas.search_schema import SearchResumesSchema, SearchVacancySchema


router = APIRouter()


@router.get('/search/search_resumes', tags=['Search'])
async def search_resumes(session: session_dep, data: SearchResumesSchema = Depends(), user_id: int = Depends(get_user_token)):

    query_user = await session.execute(select(UserModel).where(UserModel.id == user_id))
    current_user = query_user.scalar_one_or_none()

    if not current_user:
        raise HTTPException(status_code=404, detail='User not found')

    if current_user.role != Role.tenant:
        raise HTTPException(status_code=403, detail='Only tenants can search resumes')

    query = select(ResumeModel)

    if data.city:
        query = query.where(ResumeModel.city.ilike(f"%{data.city}%"))

    if data.stack:
        query = query.where(ResumeModel.stack.ilike(f'%{data.stack}'))

    if data.title:
        query = query.where(ResumeModel.title.ilike(f'%{data.title}'))

    query = query.limit(data.limit).offset(data.offset)

    result = await session.execute(query)
    resumes = result.scalars().all()

    return resumes


@router.get('/search/search_vacancies', tags=['Search'])
async def search_vacancy(session: session_dep, data: SearchVacancySchema = Depends(), user_id: int = Depends(get_user_token)):

    query_user = await session.execute(select(UserModel).where(UserModel.id == user_id))
    current_user = query_user.scalar_one_or_none()

    if not current_user:
        raise HTTPException(status_code=404, detail='User not found')

    if current_user.role != Role.applicant:
        raise HTTPException(status_code=403, detail='Only applicants can search vacancies')

    query = select(VacancyModel)

    if data.city:
        query = query.where(VacancyModel.city.ilike(f"%{data.city}%"))

    if data.compensation:
        query = query.where(VacancyModel.compensation >= int(data.compensation))

    if data.title:
        query = query.where(VacancyModel.title.ilike(f'%{data.title}'))

    query = query.limit(data.limit).offset(data.offset)


    result = await session.execute(query)
    vacancies = result.scalars().all()

    return vacancies