from fastapi import HTTPException
from sqlalchemy import select
from redis.asyncio import Redis
import json
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.user import User, Role
from backend.models.vacancy import Vacancy
from backend.models.resume import Resume
from backend.schemas.search import SearchResumes, SearchVacancies


async def search_resumes_service(session: AsyncSession, data: SearchResumes, current_user: User, redis: Redis):

    if current_user.role != Role.tenant:
        raise HTTPException(status_code=403, detail='Only tenants can search resumes')

    version = await redis.get("resume_version") or "0"
    search_params = f"version:{version}_q:{data.title or ''}_city:{data.city or ''}_stack:{data.stack or ''}_limit:{data.limit}_offset:{data.offset}"
    cache_key = f"search:resumes:{search_params}"

    cached_resumes = await redis.get(cache_key)
    if cached_resumes:
        return {"resumes": json.loads(cached_resumes), "source": "cache"}

    query = select(Resume)

    if data.city:
        query = query.where(Resume.city.ilike(f"%{data.city}%"))

    if data.stack:
        query = query.where(Resume.stack.ilike(f'%{data.stack}%'))

    if data.title:
        query = query.where(Resume.title.ilike(f'%{data.title}%'))

    query = query.limit(data.limit).offset(data.offset)

    result = await session.execute(query)
    resumes = result.scalars().all()

    resumes_json = [r.resumes_to_dict() for r in resumes]
    await redis.set(cache_key, json.dumps(resumes_json), ex=300)

    return {"resumes": resumes_json, "source": "db"}


async def search_vacancies_service(session: AsyncSession, data: SearchVacancies, current_user: User, redis: Redis):
    
    if current_user.role != Role.applicant:
        raise HTTPException(status_code=403, detail='Only applicants can search vacancies')

    version = await redis.get("vacancy_version") or "0"
    search_params = f"version:{version}_q:{data.title or ''}_city:{data.city or ''}_compensation:{data.compensation or ''}_limit:{data.limit}_offset:{data.offset}"
    cache_key = f"search:vacancies:{search_params}"

    cached_vacancies = await redis.get(cache_key)
    if cached_vacancies:
        return {"vacancies": json.loads(cached_vacancies), "source": "cache"}

    query = select(Vacancy)

    if data.city:
        query = query.where(Vacancy.city.ilike(f"%{data.city}%"))

    if data.compensation:
        query = query.where(Vacancy.compensation >= int(data.compensation))

    if data.title:
        query = query.where(Vacancy.title.ilike(f'%{data.title}'))

    query = query.limit(data.limit).offset(data.offset)

    result = await session.execute(query)
    vacancies = result.scalars().all()

    vacancies_json = [v.vacancies_to_dict() for v in vacancies]
    await redis.set(cache_key, json.dumps(vacancies_json), ex=300)

    return {"vacancies": vacancies_json, "source": "db"}