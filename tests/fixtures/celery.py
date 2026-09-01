import pytest

@pytest.fixture(autouse=True)
def send_mail(mocker):
    return mocker.patch("app.backend.helpers.celery_tasks.send_mail.send_mail_task.delay")


@pytest.fixture(autouse=True)
def sync_vacancy(mocker):
    return mocker.patch("app.backend.helpers.celery_tasks.search.sync_vacancy_task.delay")

@pytest.fixture(autouse=True)
def delete_vacancy(mocker):
    return mocker.patch("app.backend.helpers.celery_tasks.search.delete_vacancy_task.delay")


@pytest.fixture(autouse=True)
def sync_resume(mocker):
    return mocker.patch("app.backend.helpers.celery_tasks.search.sync_resume_task.delay")

@pytest.fixture(autouse=True)
def delete_resume(mocker):
    return mocker.patch("app.backend.helpers.celery_tasks.search.delete_resume_task.delay")


@pytest.fixture(autouse=True)
def sync_response(mocker):
    return mocker.patch("app.backend.helpers.celery_tasks.search.sync_response_task.delay")

@pytest.fixture(autouse=True)
def delete_response(mocker):
    return mocker.patch("app.backend.helpers.celery_tasks.search.delete_response_task.delay")