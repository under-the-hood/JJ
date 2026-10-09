import pytest

from app.backend.api.responses import response_limiter, set_status_limiter
from app.backend.api.resumes import create_resume_limit
from app.backend.api.search import search_vacancy_limiter
from app.backend.api.users import password_limit, login_limit, register_limit
from app.backend.api.vacancies import create_vacancy_limit
from app.main import app


@pytest.fixture(scope='session', autouse=True)
async def disable_all_limits():
    def skip():
        return None

    limiters = [
        register_limit,
        login_limit,
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
