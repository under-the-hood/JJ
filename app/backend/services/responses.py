from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.models.response import Response
from app.backend.models.user import User, Role
from app.backend.models.resume import Resume
from app.backend.models.vacancy import Vacancy
from app.backend.helpers.resume import check_resume_owner_helper
from app.backend.helpers.vacancy import check_vacancy_owner_helper
from app.backend.models.mails import Mails
from app.backend.schemas.response import ResponseSchema, SetStatus, SearchResponses
from app.backend.helpers.celery_tasks.send_mail import send_mail_task
from app.backend.helpers.validator import validate_user_role
from app.backend.helpers.celery_tasks.search import sync_response_task, delete_response_task
from app.backend.utils.search import meili


async def send_response_to_vacancy(session: AsyncSession, data: ResponseSchema, current_vacancy: Vacancy, current_user: User):

    validate_user_role(current_user, Role.applicant, "Only applicant can apply to vacancy")

    query_check = await session.execute(select(Response).where(Response.resume_id == data.resume_id, Response.vacancy_id == current_vacancy.id))

    if query_check.scalar_one_or_none():
        raise HTTPException(status_code=400, detail='You have already applied to this vacancy with this resume')

    response = Response(**data.model_dump())
    response.applicant_id = current_user.id
    response.vacancy_id = current_vacancy.id

    current_resume = await check_resume_owner_helper(session, data.resume_id, current_user.id)
    
    session.add(response)

    mail = Mails(
        recipient_id = current_vacancy.tenant_id,
        subject = "New response to your vacancy!",
        body = f"User {current_user.name} has responded to your vacancy!\n His resume:\ntitle: {current_resume.title}\nstack: {current_resume.stack}\ncity: {current_resume.city}"
    )

    session.add(mail)
    await session.commit()
    await session.refresh(mail)

    sync_response_task.delay(response.id)
    send_mail_task.delay(mail.id)

    return response


async def search_responses(session: AsyncSession, data: SearchResponses, current_user: User):
    filters = []
    
    if current_user.role != Role.admin:
        if not data.vacancy_id:
            raise HTTPException(status_code=400, detail="Tenant must specify vacancy_id for searching responses")
        
        await check_vacancy_owner_helper(session, data.vacancy_id, current_user.id)
        filters.append(f"vacancy_id = {data.vacancy_id}")
    else:
        if data.vacancy_id:
            filters.append(f"vacancy_id = {data.vacancy_id}")

    search_options = {
        "limit": data.limit,
        "offset": data.offset
    }

    query_parts = []
    if data.title:
        query_parts.append(data.title.strip())

    if data.stack:
        query_parts.append(data.stack.strip())

    if data.status:
        filters.append(f"status = '{data.status}'")

    if filters:
        search_options["filter"] = filters

    query_text = " ".join(query_parts)

    result = meili.index("responses").search(query_text, search_options)
    responses = result["hits"]

    total = result.get("estimatedTotalHits", len(responses))

    return responses, total, "db"


async def get_my_responses(session: AsyncSession, current_user: User):
    
    validate_user_role(current_user, Role.applicant, "You are not an applicant")

    query = await session.execute(select(Response).options(joinedload(Response.resume), joinedload(Response.vacancy)).where(Response.applicant_id == current_user.id))
    responses = query.scalars().all()

    return responses


async def delete_response(session: AsyncSession, current_response: Response, current_user: User):
    validate_user_role(current_user, Role.applicant, "Only applicant can delete their own responses")
    
    delete_response_task.delay(current_response.id)
    await session.delete(current_response)
    await session.commit()


async def set_status(session: AsyncSession, data: SetStatus, current_response: Response, current_user: User):
    
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

    sync_response_task.delay(current_response.id)
    send_mail_task.delay(mail.id)

    return current_response