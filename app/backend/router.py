from fastapi import APIRouter

from app.backend.api.users import router as users
from app.backend.api.vacancies import router as vacancies
from app.backend.api.resumes import router as resumes
from app.backend.api.responses import router as responses
from app.backend.api.search import router as search
from app.backend.api.invitation import router as invitation
from app.backend.api.admin.users import router as admin_users


main_router = APIRouter()

main_router.include_router(users)
main_router.include_router(vacancies)
main_router.include_router(resumes)
main_router.include_router(responses)
main_router.include_router(search)
main_router.include_router(invitation)
main_router.include_router(admin_users, prefix="/admin")