import tests.fixtures.meilisearch_container as meilisearch_container

def pytest_sessionfinish(session, exitstatus):
    meilisearch_container.stop()

pytest_plugins = [
    "tests.fixtures.celery",
    "tests.fixtures.client",
    "tests.fixtures.database",
    "tests.fixtures.invitation",
    "tests.fixtures.limiter",
    "tests.fixtures.meilisearch",
    "tests.fixtures.meilisearch_container",
    "tests.fixtures.redis",
    "tests.fixtures.responses",
    "tests.fixtures.resumes",
    "tests.fixtures.vacancies"
]