from fastapi import APIRouter

from app.backend.api.user import router as user_router
from app.backend.api.vacancy import router as vacancy_router
from app.backend.api.resume import router as resume_router
from app.backend.api.response import router as response_router
from app.backend.api.search import router as search_router
from app.backend.api.admin import router as admin_router


main_router = APIRouter()

main_router.include_router(user_router)
main_router.include_router(vacancy_router)
main_router.include_router(resume_router)
main_router.include_router(response_router)
main_router.include_router(search_router)
main_router.include_router(admin_router)