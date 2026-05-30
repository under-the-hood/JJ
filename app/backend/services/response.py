from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.models.response import Response
from app.backend.models.user import User, Role
from app.backend.models.vacancy import Vacancy
from app.backend.models.resume import Resume
from app.backend.models.mails import Mails
from app.backend.schemas.response import ResponseSchema, SetStatus
from app.backend.utils.celery_tasks import send_mail_task
from app.backend.utils.helpers import validate_user_role


async def send_response_to_vacancy(session: AsyncSession, data: ResponseSchema, current_vacancy: Vacancy, current_resume: Resume, current_user: User):

    validate_user_role(current_user, Role.applicant, "Only applicant can apply to vacancy")

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
        subject = "New response to your vacancy!",
        body = f"User {current_user.name} has responsed to your vacancy! His resume:\ntitle: {current_resume.title}\nstack: {current_resume.stack}\ncity: {current_resume.city}"
    )

    session.add(mail)
    await session.commit()
    await session.refresh(mail)

    send_mail_task.delay(mail.id)

    return response


async def get_responses_to_vacancy(session: AsyncSession, current_vacancy: Vacancy, current_user: User):
    
    validate_user_role(current_user, Role.tenant, "You are not a tenant")

    query_responses = await session.execute(select(Response).options(joinedload(Response.resume), joinedload(Response.user)).where(Response.vacancy_id == current_vacancy.id))

    all_resumes = query_responses.scalars().all()

    return all_resumes


async def set_status_to_response(session: AsyncSession, data: SetStatus, current_response: Response, current_user: User):
    
    validate_user_role(current_user, Role.tenant, "Only tenants can set status to responses")
    current_response.status = data.status

    mail = Mails(
        recipient_id = current_response.applicant_id,
        subject = "Application Status Updated",
        body = f"Hello!\nYour application status for {current_response.vacancy.title} has been updated to {current_response.status}."
    )

    session.add(mail)
    await session.commit()
    await session.refresh(current_response)
    await session.refresh(mail)

    send_mail_task.delay(mail.id)

    return current_response