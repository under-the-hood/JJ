import pytest

@pytest.fixture
def send_response_to_vacancy(applicant_client, create_vacancy, create_resume):
    async def create_response():
        cover_letter = {
            "resume_id": create_resume,
            "cover_letter": "Hello! I want work in your company!",
        }

        response = await applicant_client.post(f"/responses/vacancies/{create_vacancy}", params={"resume_id": create_resume}, json=cover_letter)

        data = response.json()
        response_id = data["Response"]["id"]

        return response_id
    return create_response