from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from app.backend.models.user import User
from app.backend.helpers.celery_tasks.send_mail import send_mail_task
from app.backend.schemas.invitations import InvitationSchema
from app.backend.models.invitations import Invitation
from app.backend.helpers.vacancy import check_vacancy_owner
from app.backend.models.mails import Mails
from app.backend.models.resume import Resume
from app.backend.helpers.vacancy import get_vacancy


async def send_interview_invitation(session: AsyncSession, data: InvitationSchema, current_resume: Resume, current_user: User):
    query_check = await session.execute(select(Invitation).where(Invitation.resume_id == current_resume.id, Invitation.vacancy_id == data.vacancy_id))
    if query_check.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="You have already sent interview invitation to this resume")

    applicant_id = current_resume.applicant_id
    
    current_vacancy = await check_vacancy_owner(session, data.vacancy_id, current_user.id)
    
    invitation = Invitation(**data.model_dump())
    invitation.applicant_id = applicant_id
    invitation.tenant_id = current_user.id
    invitation.resume_id = current_resume.id

    session.add(invitation)

    mail = Mails(
        recipient_id = applicant_id,
        subject = f"You have been invited to an interview!\nTenant {current_user.name} invited you to an interview\nVacancy:\ntitle: {current_vacancy.title}\ncompenstation: {current_vacancy.compensation}",
        body = data.cover_letter
    )

    session.add(mail)
    await session.commit()
    await session.refresh(mail)

    send_mail_task.delay(mail.id)

    return invitation


async def delete_invitation(session: AsyncSession, current_invitation: Invitation, current_user: User):
    await session.delete(current_invitation)
    await session.commit()