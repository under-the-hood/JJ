import traceback
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.response import Response
from backend.models.user import User, Role
from backend.models.vacancy import Vacancy
from backend.models.resume import Resume
from backend.models.mails import Mails
from backend.schemas.response import ResponseSchema, SetStatus
from backend.utils.celery_tasks import send_mail_task


async def send_response_to_vacancy(data: ResponseSchema, session: AsyncSession, current_vacancy: Vacancy, current_resume: Resume, current_user: User):
    
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

    mail = Mails(
        recipient_id = current_vacancy.tenant_id,
        subject = "New response to your vacncy!",
        body = f"User {current_user.name} has responsed to your vacancy! His resume:\ntitle: {current_resume.title}\nstack: {current_resume.stack}\ncity: {current_resume.city}"
    )

    session.add(mail)
    await session.commit()

    send_mail_task.delay(mail.id)

    return response


async def get_responses_to_vacancy(session: AsyncSession, current_vacancy: Vacancy, current_user: User):
    
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


async def set_status_to_response(response_id: int, data: SetStatus, session: AsyncSession, current_user: User):
    
    if current_user.role != Role.tenant:
        raise HTTPException(status_code=403, detail='Only tenants can set status to responses')

    query_response = await session.execute(select(Response).options(joinedload(Response.vacancy)).where(Response.id == response_id))
    current_response = query_response.scalar_one_or_none()

    if not current_response:
        raise HTTPException(status_code=404, detail='Response not found')

    if current_user.id != current_response.vacancy.tenant_id:
        raise HTTPException(status_code=403, detail="It's not your vacancy")

    current_response.status = data.status

    mail = Mails(
        recipient_id = current_response.applicant_id,
        subject = "Application Status Updated",
        body = f"Hello!\nYour application status for {current_response.vacancy.title} has been updated to {current_response.status}."
    )

    session.add(mail)
    await session.commit()
    await session.refresh(current_response)

    send_mail_task.delay(mail.id)

    return current_response