from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select

from backend.models.models import VacancyModel, UserModel, Role
from backend.schemas.vacancy_schema import CreateVacancySchema, EditVacancySchema
from backend.database.database import session_dep
from backend.dependencies import get_user_token, check_user, check_vacancy


router = APIRouter()


@router.post('/vacancy/create_vacancy', tags=['Vacancy'])
async def create_vacancy(data: CreateVacancySchema, session: session_dep, current_user: int = Depends(check_user)):

    if current_user.role != Role.tenant:
        raise HTTPException(status_code=403, detail='Only tenants can make vacancies')

    new_vacancy = VacancyModel(**data.model_dump())
    new_vacancy.tenant_id = current_user.id

    session.add(new_vacancy)
    await session.commit()

    return {'success': True, 'message': 'Vacancy was created', 'Vacancy': new_vacancy}


@router.get('/vacancy/get_all_my_vacancies', tags=['Vacancy'])
async def get_all_my_vacancies(session: session_dep, current_user: int = Depends(check_user)):

    vacancy_query = await session.execute(select(VacancyModel).where(VacancyModel.tenant_id == current_user.id))
    all_vacancies = vacancy_query.scalars().all()

    return {'success': True, 'Your vacancies': all_vacancies}


@router.put('/vacancy/edit_vacancy/{vacancy_id}', tags=['Vacancy'])
async def edit_vacancy(session: session_dep, current_vacancy: int = Depends(check_vacancy), data: EditVacancySchema = Depends(), current_user: int = Depends(check_user)):

    if current_user.role != Role.tenant:
        raise HTTPException(status_code=403, detail='Only applicant can edit resume')

    if current_user.id != current_vacancy.tenant_id:
        raise HTTPException(status_code=403, detail="It's not your resume")

    if data.new_title:
        current_vacancy.title = data.new_title

    if data.new_city:
        current_vacancy.city = data.new_city

    if data.new_compensation:
        current_vacancy.compensation = data.new_compensation

    await session.commit()
    await session.refresh(current_vacancy)

    return {'success': True, 'message': 'Vacancy was edited'}


@router.delete('/vacancy/delete_vacancy/{vacancy_id}', tags=['Vacancy'])
async def delete_vacancy(session: session_dep, current_vacancy: int = Depends(check_vacancy), current_user: int = Depends(check_user)):

    if current_user.role != Role.tenant:
        raise HTTPException(status_code=403, detail='Only tenants can delete vacancy')

    if current_vacancy.tenant_id != current_user.id:
        raise HTTPException(status_code=403, detail='This is not your vacancy')

    await session.delete(current_vacancy)
    await session.commit()

    return {'success': True, 'message': 'Vacancy was deleted'}