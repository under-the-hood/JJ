import pytest

from app.main import app
from app.backend.api.responses import set_status_limiter, response_limiter
from app.backend.api.users import password_limit, sign_in_limit, sign_up_limit
from app.backend.api.search import search_vacancy_limiter
from app.backend.api.resumes import create_resume_limit
from app.backend.api.vacancies import create_vacancy_limit


@pytest.fixture(scope='session', autouse=True)
async def disable_all_limits():
    skip = lambda: None

    limiters = [
        sign_up_limit,
        sign_in_limit, 
        password_limit, 
        set_status_limiter, 
        response_limiter, 
        search_vacancy_limiter, 
        create_vacancy_limit, 
        create_resume_limit
        ]

    for lim in limiters:
        app.dependency_overrides[lim] = skip

    yield