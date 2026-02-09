from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from redis.asyncio import Redis
import json

from backend.dependencies import get_user_token
from backend.database.database import session_dep
from backend.models.models import ResumeModel, UserModel, Role, VacancyModel
from backend.schemas.search_schema import SearchResumesSchema, SearchVacancySchema
from backend.database.limiter import rate_limiter_factory
from backend.database.redis_database import get_redis


router = APIRouter()


search_resumes_limiter = rate_limiter_factory("/search/search_resumes", 5, 60)

@router.get('/search/search_resumes', tags=['Search'], dependencies=[Depends(search_resumes_limiter)])
async def search_resumes(session: session_dep, data: SearchResumesSchema = Depends(), user_id: int = Depends(get_user_token), redis: Redis = Depends(get_redis)):

    query_user = await session.execute(select(UserModel).where(UserModel.id == user_id))
    current_user = query_user.scalar_one_or_none()

    if not current_user:
        raise HTTPException(status_code=404, detail='User not found')

    if current_user.role != Role.tenant:
        raise HTTPException(status_code=403, detail='Only tenants can search resumes')

    version = await redis.get("resume_version") or "0"
    search_params = f"version:{version}_q:{data.title or ''}_city:{data.city or ''}_stack:{data.stack or ''}_limit:{data.limit}_offset:{data.offset}"
    cache_key = f"search:resumes:{search_params}"

    cached_resumes = await redis.get(cache_key)
    if cached_resumes:
        return {"resumes": json.loads(cached_resumes), "source": "cache"}

    query = select(ResumeModel)

    if data.city:
        query = query.where(ResumeModel.city.ilike(f"%{data.city}%"))

    if data.stack:
        query = query.where(ResumeModel.stack.ilike(f'%{data.stack}'))

    if data.title:
        query = query.where(ResumeModel.title.ilike(f'%{data.title}'))

    query = query.limit(data.limit).offset(data.offset)

    result = await session.execute(query)
    resumes = result.scalars().all()

    resumes_json = [r.resumes_to_dict() for r in resumes]
    await redis.set(cache_key, json.dumps(resumes_json), ex=300)

    return {"resumes": resumes_json, "source": "db"}


search_vacancy_limiter = rate_limiter_factory("/search/search_vacancies", 5, 60)

@router.get('/search/search_vacancies', tags=['Search'], dependencies=[Depends(search_vacancy_limiter)])
async def search_vacancies(session: session_dep, data: SearchVacancySchema = Depends(), user_id: int = Depends(get_user_token), redis: Redis = Depends(get_redis)):

    query_user = await session.execute(select(UserModel).where(UserModel.id == user_id))
    current_user = query_user.scalar_one_or_none()

    if not current_user:
        raise HTTPException(status_code=404, detail='User not found')

    if current_user.role != Role.applicant:
        raise HTTPException(status_code=403, detail='Only applicants can search vacancies')

    version = await redis.get("vacancy_version") or "0"
    search_params = f"version:{version}_q:{data.title or ''}_city:{data.city or ''}_compensation:{data.compensation or ''}_limit:{data.limit}_offset:{data.offset}"
    cache_key = f"search:vacancies:{search_params}"

    cached_vacancies = await redis.get(cache_key)
    if cached_vacancies:
        return {"vacancies": json.loads(cached_vacancies), "source": "cache"}

    query = select(VacancyModel)

    if data.city:
        query = query.where(VacancyModel.city.ilike(f"%{data.city}%"))

    if data.compensation:
        query = query.where(VacancyModel.compensation >= int(data.compensation))

    if data.title:
        query = query.where(VacancyModel.title.ilike(f'%{data.title}'))

    query = query.limit(data.limit).offset(data.offset)

    result = await session.execute(query)
    vacancies = result.scalars().all()

    vacancies_json = [v.vacancies_to_dict() for v in vacancies]
    await redis.set(cache_key, json.dumps(vacancies_json), ex=300)

    return {"vacancies": vacancies_json, "source": "db"}