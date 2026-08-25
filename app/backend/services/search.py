from sqlalchemy import select, and_
from redis.asyncio import Redis
import json
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.models.user import User, Role
from app.backend.models.vacancy import Vacancy
from app.backend.models.resume import Resume
from app.backend.schemas.search import SearchResumes, SearchVacancies
from app.backend.utils.search import meili


async def search_resumes(session: AsyncSession, data: SearchResumes, current_user: User, redis: Redis):

    version = await redis.get("resume_version") or "0"
    search_params = f"version:{version}_q:{data.title or ''}_city:{data.city or ''}_stack:{data.stack or ''}_limit:{data.limit}_offset:{data.offset}"
    cache_key = f"search:resumes:{search_params}"

    cached_resumes = await redis.get(cache_key)
    if cached_resumes:
        return json.loads(cached_resumes), "cache"

    search_options = {
        "limit": data.limit,
        "offset": data.offset
    }

    query_parts = []
    if data.title:
        query_parts.append(data.title.strip())

    if data.city:
        query_parts.append(data.city.strip())

    if data.stack:
        query_parts.append(data.stack.strip())

    query_text = " ".join(query_parts)

    result = meili.index("resumes").search(query_text, search_options)
    resumes = result["hits"]

    await redis.set(cache_key, json.dumps(resumes), ex=300)

    return resumes, "db"


async def search_vacancies(session: AsyncSession, data: SearchVacancies, current_user: User, redis: Redis):

    version = await redis.get("vacancy_version") or "0"
    search_params = f"version:{version}_q:{data.title or ''}_city:{data.city or ''}_compensation:{data.compensation or ''}_limit:{data.limit}_offset:{data.offset}"
    cache_key = f"search:vacancies:{search_params}"

    cached_vacancies = await redis.get(cache_key)
    if cached_vacancies:
        return json.loads(cached_vacancies), "cache"

    search_options = {
        "limit": data.limit,
        "offset": data.offset
    }

    query_parts = []
    if data.title:
        query_parts.append(data.title.strip())

    if data.city:
        query_parts.append(data.city.strip())

    query_text = " ".join(query_parts)

    filters = []
    if data.compensation:
        filters.append(f"compensation >= {data.compensation}")

    if filters:
        search_options["filter"] = filters

    result = meili.index("vacancies").search(query_text, search_options)
    vacancies = result["hits"]

    await redis.set(cache_key, json.dumps(vacancies), ex=300)

    return vacancies, "db"