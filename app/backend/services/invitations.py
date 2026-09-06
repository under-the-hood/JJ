from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from app.backend.models.user import User, Role
from app.backend.helpers.celery_tasks.send_mail import send_mail_task
from app.backend.schemas.invitations import InvitationSchema, SearchInvitation
from app.backend.models.invitations import Invitation
from app.backend.helpers.vacancy import check_vacancy_owner
from app.backend.utils.meilisearch.client import meili
from app.backend.models.mails import Mails
from app.backend.models.resume import Resume
from app.backend.helpers.celery_tasks.meilisearch.invitation import sync_invitation_task, delete_invitation_task


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
        subject = f"You have been invited to an interview!",
        body = (
            f"Tenant {current_user.name} invited you to an interview\n"
            f"Vacancy:\ntitle: {current_vacancy.title}\ncompensation: {current_vacancy.compensation}\n\n"
            f"Cover letter:\n{data.cover_letter}"
        )
    )

    session.add(mail)
    await session.commit()
    await session.refresh(mail)

    sync_invitation_task.delay(invitation.id)
    send_mail_task.delay(mail.id)

    return invitation


async def delete_invitation(session: AsyncSession, current_invitation: Invitation, current_user: User):
    delete_invitation_task.delay(current_invitation.id)

    await session.delete(current_invitation)
    await session.commit()


async def search_invitations(data: SearchInvitation, current_user: User):
    filters = []

    if current_user.role == Role.tenant:
        filters.append(f"tenant_id = {current_user.id}")
    
    if current_user.role == Role.applicant:
        filters.append(f"applicant_id = {current_user.id}")

    if current_user.role == Role.admin:
        if data.vacancy_id:
            filters.append(f"vacancy_id = {data.vacancy_id}")
        if data.resume_id:
            filters.append(f"resume_id = {data.resume_id}")
        if data.applicant_id:
            filters.append(f"applicant_id = {data.applicant_id}")
        if data.tenant_id:
            filters.append(f"tenant_id = {data.tenant_id}")

    search_options = {
        "limit": data.limit,
        "offset": data.offset
    }

    query_parts = []
    if data.resume_title:
        query_parts.append(data.resume_title.strip())

    if data.resume_stack:
        query_parts.append(data.resume_stack.strip())

    if data.vacancy_title:
        query_parts.append(data.vacancy_title.strip())

    if filters:
        search_options["filter"] = filters

    query_text = " ".join(query_parts)

    result = meili.index("invitations").search(query_text, search_options)
    invitations = result["hits"]

    total = result.get("estimatedTotalHits", len(invitations))

    return invitations, total