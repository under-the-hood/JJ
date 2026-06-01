from sqlalchemy import select, and_
from redis.asyncio import Redis
import json
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.models.user import User
from app.backend.models.vacancy import Vacancy
from app.backend.models.resume import Resume
from app.backend.schemas.search import SearchResumes, SearchVacancies
from app.backend.utils.search import apply_words_filter


async def search_resumes_service(session: AsyncSession, data: SearchResumes, current_user: User, redis: Redis):

    version = await redis.get("resume_version") or "0"
    search_params = f"version:{version}_q:{data.title or ''}_city:{data.city or ''}_stack:{data.stack or ''}_limit:{data.limit}_offset:{data.offset}"
    cache_key = f"search:resumes:{search_params}"

    cached_resumes = await redis.get(cache_key)
    if cached_resumes:
        return {"resumes": json.loads(cached_resumes), "source": "cache"}

    query = select(Resume)

    if data.city:
        query = query.where(apply_words_filter(Resume.city, data.city))

    if data.title:
        words = data.title.strip().split()
        conditions = []
        for word in words:
            condition = Resume.title.ilike(f"%{word}%")
            conditions.append(condition)
        query = query.where(and_(*conditions))
    
    if data.stack:
        words = data.stack.strip().split()
        conditions = []
        for word in words:
            condition = Resume.stack.ilike(f"%{word}%")
            conditions.append(condition)
        query = query.where(and_(*conditions))

    query = query.limit(data.limit).offset(data.offset)

    result = await session.execute(query)
    resumes = result.scalars().all()

    resumes_json = [r.resumes_to_dict() for r in resumes]
    await redis.set(cache_key, json.dumps(resumes_json), ex=300)

    return {"resumes": resumes_json, "source": "db"}


async def search_vacancies_service(session: AsyncSession, data: SearchVacancies, current_user: User, redis: Redis):

    version = await redis.get("vacancy_version") or "0"
    search_params = f"version:{version}_q:{data.title or ''}_city:{data.city or ''}_compensation:{data.compensation or ''}_limit:{data.limit}_offset:{data.offset}"
    cache_key = f"search:vacancies:{search_params}"

    cached_vacancies = await redis.get(cache_key)
    if cached_vacancies:
        return {"vacancies": json.loads(cached_vacancies), "source": "cache"}

    query = select(Vacancy)

    if data.title:
        words = data.title.strip().split()
        conditions = []
        for word in words:
            condition = Vacancy.title.ilike(f"%{word}%")
            conditions.append(condition)
        query = query.where(and_(*conditions))

    if data.compensation:
        words = data.compensation.strip().split()
        conditions = []
        for word in words:
            condition = Vacancy.compensation.ilike(f"%{word}%")
            conditions.append(condition)
        query = query.where(and_(*conditions))
    
    if data.city:
        words = data.city.strip().split()
        conditions = []
        for word in words:
            condition = Vacancy.city.ilike(f"%{word}%")
            conditions.append(condition)
        query = query.where(and_(*conditions))

    query = query.limit(data.limit).offset(data.offset)

    result = await session.execute(query)
    vacancies = result.scalars().all()

    vacancies_json = [v.vacancies_to_dict() for v in vacancies]
    await redis.set(cache_key, json.dumps(vacancies_json), ex=300)

    return {"vacancies": vacancies_json, "source": "db"}