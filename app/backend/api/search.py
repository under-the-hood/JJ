from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from app.backend.dependencies.vacancy import check_tenant
from app.backend.dependencies.resume import check_applicant
from app.backend.database.database import session_dep
from app.backend.models.user import User
from app.backend.schemas.search import SearchResumes, SearchVacancies
from app.backend.utils.limiter import rate_limiter_factory
from app.backend.database.redis_database import get_redis
from app.backend.services.search import search_resumes_service, search_vacancies_service


router = APIRouter()


search_resumes_limiter = rate_limiter_factory("/search/search_resumes", 5, 60)

@router.get('/search/search_resumes', tags=['Search'], dependencies=[Depends(search_resumes_limiter)])
async def search_resumes(session: session_dep, data: SearchResumes = Depends(), current_user: User = Depends(check_tenant), redis: Redis = Depends(get_redis)):
    return await search_resumes_service(session=session, data=data, current_user=current_user, redis=redis)


search_vacancy_limiter = rate_limiter_factory("/search/search_vacancies", 5, 60)

@router.get('/search/search_vacancies', tags=['Search'], dependencies=[Depends(search_vacancy_limiter)])
async def search_vacancies(session: session_dep, data: SearchVacancies = Depends(), current_user: User = Depends(check_applicant), redis: Redis = Depends(get_redis)):
    return await search_vacancies_service(session=session, data=data, current_user=current_user, redis=redis)