from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from redis.asyncio import Redis

from backend.models.models import UserModel, ResumeModel, Role
from backend.database.database import session_dep
from backend.schemas.resume_schema import CreateResumeSchema, EditResumeSchema
from backend.dependencies import check_user, check_resume
from backend.database.redis_database import get_redis


router = APIRouter()


@router.post('/resume/create_resume', tags=['Resume'])
async def create_resume(data: CreateResumeSchema, session: session_dep, current_user: UserModel = Depends(check_user), redis: Redis = Depends(get_redis)):

    if current_user.role != Role.applicant:
        raise HTTPException(status_code=403, detail='Only applicant can make resumes')

    new_resume = ResumeModel(**data.model_dump())

    new_resume.applicant_id = current_user.id

    session.add(new_resume)
    await session.commit()

    await redis.incr("resume_version")

    return {'success': True, 'message': 'Resume was created', "Resume": new_resume}


@router.get('/resume/get_all_my_resumes', tags=['Resume'])
async def get_all_resumes(session: session_dep, current_user: UserModel = Depends(check_user)):

    resume_query = await session.execute(select(ResumeModel).where(ResumeModel.applicant_id == current_user.id))
    all_resumes = resume_query.scalars().all()

    return {'success': True, 'Your resumes': all_resumes}


@router.put('/resume/edit_resume/{resume_id}', tags=['Resume'])
async def edit_resume(session: session_dep, current_resume: ResumeModel = Depends(check_resume), data: EditResumeSchema = Depends(), current_user: UserModel = Depends(check_user), redis: Redis = Depends(get_redis)):

    if current_user.role != Role.applicant:
        raise HTTPException(status_code=403, detail='Only applicant can edit resume')

    if current_user.id != current_resume.applicant_id:
        raise HTTPException(status_code=403, detail="It's not your resume")

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

    await redis.incr("resume_version")

    return {'success': True, 'message': 'Resume was edited'}


@router.delete('/resume/delete_resume/{resume_id}', tags=['Resume'])
async def delete_resume(session: session_dep, current_resume: ResumeModel = Depends(check_resume), current_user: UserModel = Depends(check_user), redis: Redis = Depends(get_redis)):

    if current_user.role != Role.applicant:
        raise HTTPException(status_code=403, detail='Only applicant can edit resumes')

    if current_user.id != current_resume.applicant_id:
        raise HTTPException(status_code=403, detail='This is not your resume')

    await session.delete(current_resume)
    await session.commit()

    await redis.incr("resume_version")

    return {'success': True, 'message': 'Resume was deleted'}