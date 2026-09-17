from tests.fixtures import meilisearch_container


def pytest_sessionfinish(session, exitstatus):
    meilisearch_container.stop()

pytest_plugins = [
    "tests.fixtures.celery",
    "tests.fixtures.client",
    "tests.fixtures.database",
    "tests.fixtures.invitations",
    "tests.fixtures.limiter",
    "tests.fixtures.meilisearch",
    "tests.fixtures.meilisearch_container",
    "tests.fixtures.redis",
    "tests.fixtures.responses",
    "tests.fixtures.resumes",
    "tests.fixtures.users",
    "tests.fixtures.vacancies"
]
