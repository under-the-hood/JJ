from fastapi import APIRouter, Depends

from app.backend.dependencies.vacancy import check_tenant_or_admin
from app.backend.dependencies.resume import check_applicant_or_admin
from app.backend.models.user import User
from app.backend.schemas.search import SearchResumes, SearchVacancies
from app.backend.helpers.rate_limiter import rate_limiter_factory
import app.backend.services.search as search_service


router = APIRouter(prefix="/search", tags=['Search'])

search_resumes_limiter = rate_limiter_factory("/search/resumes", 5, 60)

@router.get('/resumes', dependencies=[Depends(search_resumes_limiter)])
async def search_resumes(data: SearchResumes = Depends(), current_user: User = Depends(check_tenant_or_admin)):
    all_resumes, total  = await search_service.search_resumes(data=data, current_user=current_user)
    return {"resumes": all_resumes, "total": total}


search_vacancy_limiter = rate_limiter_factory("/search/vacancies", 5, 60)

@router.get('/vacancies', dependencies=[Depends(search_vacancy_limiter)])
async def search_vacancies(data: SearchVacancies = Depends(), current_user: User = Depends(check_applicant_or_admin)):
    all_vacancies, total = await search_service.search_vacancies(data=data, current_user=current_user)
    return {"vacancies": all_vacancies, "total": total}