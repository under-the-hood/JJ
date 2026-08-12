import pytest

@pytest.fixture(scope="function")
def mock_celery(mocker):
    return mocker.patch("app.backend.helpers.celery_tasks.send_mail_task.delay")