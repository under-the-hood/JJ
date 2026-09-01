import pytest

@pytest.fixture
def send_interview_invitation(tenant_client, create_resume, create_vacancy):
    async def create_invitation():
        json = {
            "vacancy_id": create_vacancy,
            "cover_letter": "Hello! We invite you to an interview"
        }
        response = await tenant_client.post(f"/invitation/interview/{create_resume}", json=json)
        assert response.status_code == 200

        invitation_id = response.json()["invitation"]["id"]

        return invitation_id
    return create_invitation