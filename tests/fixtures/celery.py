import pytest

@pytest.fixture(autouse=True)
def send_mail(mocker):
    return mocker.patch("app.backend.helpers.celery_tasks.send_mail.send_mail_task.delay")