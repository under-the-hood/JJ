from fastapi import APIRouter

from app.backend.api.users import router as users
from app.backend.api.vacancies import router as vacancies
from app.backend.api.resumes import router as resumes
from app.backend.api.responses import router as responses
from app.backend.api.search import router as search
from app.backend.api.admin.users import router as admin_users
from app.backend.api.admin.resumes import router as admin_resumes
from app.backend.api.admin.vacancies import router as admin_vacancies
from app.backend.api.admin.responses import router as admin_responses


main_router = APIRouter()

main_router.include_router(users)
main_router.include_router(vacancies)
main_router.include_router(resumes)
main_router.include_router(responses)
main_router.include_router(search)
main_router.include_router(admin_users, prefix="/admin")
main_router.include_router(admin_resumes, prefix="/admin")
main_router.include_router(admin_vacancies, prefix="/admin")
main_router.include_router(admin_responses, prefix="/admin")