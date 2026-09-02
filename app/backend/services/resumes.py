from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.models.user import User
from app.backend.models.resume import Resume
from app.backend.schemas.resume import CreateResume, EditResume
from app.backend.helpers.celery_tasks.meilisearch.resume import sync_resume_task, delete_resume_task


async def create_resume(session: AsyncSession, data: CreateResume, current_user: User):

    new_resume = Resume(**data.model_dump())

    new_resume.applicant_id = current_user.id

    session.add(new_resume)
    await session.commit()

    sync_resume_task.delay(new_resume.id)

    return new_resume


async def get_my_resumes(session: AsyncSession, current_user: User):

    resume_query = await session.execute(select(Resume).where(Resume.applicant_id == current_user.id))
    all_resumes = resume_query.scalars().all()

    return all_resumes


async def update_resume(session: AsyncSession, current_resume: Resume, data: EditResume):

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

    sync_resume_task.delay(current_resume.id)


async def delete_resume(session: AsyncSession, current_resume: Resume):
    delete_resume_task.delay(current_resume.id)

    await session.delete(current_resume)
    await session.commit()
