from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from backend.dependencies import check_user
from backend.database.database import session_dep
from backend.models.user import User
from backend.schemas.search import SearchResumes, SearchVacancies
from backend.utils.limiter import rate_limiter_factory
from backend.database.redis_database import get_redis
from backend.services.search import search_resumes_service, search_vacancies_service


router = APIRouter()


search_resumes_limiter = rate_limiter_factory("/search/search_resumes", 5, 60)

@router.get('/search/search_resumes', tags=['Search'], dependencies=[Depends(search_resumes_limiter)])
async def search_resumes(session: session_dep, data: SearchResumes = Depends(), current_user: User = Depends(check_user), redis: Redis = Depends(get_redis)):

    resumes = await search_resumes_service(session, data, current_user, redis)
    return {**resumes}


search_vacancy_limiter = rate_limiter_factory("/search/search_vacancies", 5, 60)

@router.get('/search/search_vacancies', tags=['Search'], dependencies=[Depends(search_vacancy_limiter)])
async def search_vacancies(session: session_dep, data: SearchVacancies = Depends(), current_user: User = Depends(check_user), redis: Redis = Depends(get_redis)):

    vacancies = await search_vacancies_service(session, data, current_user, redis)
    return {**vacancies}