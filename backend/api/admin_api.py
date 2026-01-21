from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func


from backend.database.database import session_dep
from backend.dependencies import check_admin, check_vacancy, check_resume, check_user_for_edit_by_admib
from backend.models.models import UserModel, Role, VacancyModel, ResumeModel, ResponseModel
from backend.schemas.admin_schema import EditUserNameByAdmin, UpdateUserRoleByAdmin
from backend.schemas.vacancy_schema import EditVacancySchema
from backend.schemas.resume_schema import EditResumeSchema


router = APIRouter()


#-------------Work with user-------------
@router.get('/admin/get_users', tags=['Admin'])
async def get_users(session: session_dep, limit: int = 10, offset: int = 0, admin: int = Depends(check_admin)):

    query = await session.execute(select(UserModel).limit(limit).offset(offset))
    users = query.scalars().all()

    quantity = await session.scalar(select(func.count(UserModel.id)))

    return {
        'quantity of all users': quantity,
        'users': users
    }


@router.put('/admin/edit_user_name/{user_id}', tags=['Admin'])
async def edit_user_name(data: EditUserNameByAdmin, session: session_dep, current_user: UserModel = Depends(check_user_for_edit_by_admib), admin: int = Depends(check_admin)):

    if current_user.id == admin.id:
        raise HTTPException(status_code=403, detail='You can not edit your own admin account')

    if current_user.role == Role.admin:
        raise HTTPException(status_code=403, detail='You can not edit accounts of other admins')

    current_user.name = data.new_name

    await session.commit()
    await session.refresh(current_user)

    return {'success': True, 'message': 'Users name was edited'}


@router.put('/admin/update_user_role/{user_id}', tags=['Admin'])
async def update_user_role(session: session_dep, data: UpdateUserRoleByAdmin, current_user: UserModel = Depends(check_user_for_edit_by_admib), admin: int = Depends(check_admin)):

    if current_user.id == admin.id:
        raise HTTPException(status_code=403, detail='You can not update your own role')

    current_user.role = data.new_role

    await session.commit()
    await session.refresh(current_user)

    return {'success': True, 'message': 'Role was updated'}    


@router.delete('/admin/delete_user/{user_id}', tags=['Admin'])
async def delete_user(session: session_dep, current_user: UserModel = Depends(check_user_for_edit_by_admib), admin: int = Depends(check_admin)):

    if current_user.id == admin.id:
        raise HTTPException(status_code=403, detail='You can not delete your own admin account')

    if current_user.role == Role.admin:
        raise HTTPException(status_code=403, detail='You can not delete other admins')

    await session.delete(current_user)
    await session.commit()

    return {'success': True, 'message': 'User was deleted'}


#-------------Work with vacancy-------------
@router.put('/admin/edit_vacancy/{vacancy_id}', tags=['Admin'])
async def edit_vacancy(session: session_dep, current_vacancy: VacancyModel = Depends(check_vacancy), data: EditVacancySchema = Depends(), admin: int = Depends(check_admin)):

    if data.new_title:
        current_vacancy.title = data.new_title

    if data.new_city:
        current_vacancy.city = data.new_city

    if data.new_compensation:
        current_vacancy.compensation = data.new_compensation

    await session.commit()
    await session.refresh(current_vacancy)

    return {'success': True, 'message': 'Vacancy was edited'}


@router.get('/admin/get_vacancies', tags=['Admin'])
async def get_vacancies(session: session_dep, limit: int = 10, offset: int = 0, admin: int = Depends(check_admin)):

    query = await session.execute(select(VacancyModel).limit(limit).offset(offset))
    vacancies = query.scalars().all()

    quantity = await session.scalar(select(func.count(VacancyModel.id)))

    return {
        'quantity of all vacancies': quantity,
        'vacancies': vacancies
    }


@router.delete('/admin/delete_vacancy/{vacancy_id}', tags=['Admin'])
async def delete_vacancy(session: session_dep, current_vacancy: VacancyModel = Depends(check_vacancy), admin: int = Depends(check_admin)):

    await session.delete(current_vacancy)
    await session.commit()

    return {'success': True, 'message': 'Vacancy was deleted'}


#-------------Work with resume-------------
@router.put('/admin/edit_resume/{resume_id}', tags=['Admin'])
async def edit_resume(session: session_dep, current_resume: ResumeModel = Depends(check_resume), data: EditResumeSchema = Depends(), admin: int = Depends(check_admin)):

    if data.new_title:
        current_resume.title = data.new_title

    if data.new_about:
        current_resume.about = data.new_about

    if data.new_city:
        current_resume.city = data.new_city

    if data.new_stack:
        current_resume.stack = data.new_stack

    await session.commit()
    await session.refresh(current_resume)

    return {'success': True, 'message': 'Resume was edited'}


@router.get('/admin/get_resumes', tags=['Admin'])
async def get_resumes(session: session_dep, limit: int = 10, offset: int = 0, admin: int = Depends(check_admin)):

    query = await session.execute(select(ResumeModel).limit(limit).offset(offset))
    resumes = query.scalars().all()

    quantity = await session.scalar(select(func.count(ResumeModel.id)))

    return {
        'quantity of all resumes': quantity,
        'resumes': resumes
    }


@router.delete('/admin/delete_resume/{resume_id}', tags=['Admin'])
async def delete_resume(session: session_dep, current_resume: ResumeModel = Depends(check_resume), admin: int = Depends(check_admin)):

    await session.delete(current_resume)
    await session.commit()

    return {'success': True, 'message': 'Resume was deleted'}


#-------------Work with responses-------------
@router.get('/admin/get_responses', tags=['Admin'])
async def get_responses(session: session_dep, limit: int = 10, offset: int = 0, admin: int = Depends(check_admin)):

    query = await session.execute(select(ResponseModel).limit(limit).offset(offset))    
    responses = query.scalars().all()
    quantity = await session.scalar(select(func.count(ResponseModel.id)))

    return {
        'quantity of all responses': quantity,
        'responses': responses
        }


@router.delete('/admin/delete_response/{response_id}', tags=['Admin'])
async def delete_response(response_id: int, session: session_dep, admin: int = Depends(check_admin)):

    query = await session.execute(select(ResponseModel).where(ResponseModel.id == response_id))
    current_response = query.scalar_one_or_none()

    if not current_response:
        raise HTTPException(status_code=404, detail='Response not found')

    await session.delete(current_response)
    await session.commit()

    return {'success': True, 'message': 'Response was deleted'}