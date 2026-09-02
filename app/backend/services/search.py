from app.backend.models.user import User
from app.backend.schemas.search import SearchResumes, SearchVacancies
from app.backend.utils.meilisearch.client import meili


async def search_resumes(data: SearchResumes, current_user: User):
    search_options = {
        "limit": data.limit,
        "offset": data.offset
    }

    query_parts = []
    if data.title:
        query_parts.append(data.title.strip())

    if data.city:
        query_parts.append(data.city.strip())

    if data.stack:
        query_parts.append(data.stack.strip())

    query_text = " ".join(query_parts)

    result = meili.index("resumes").search(query_text, search_options)
    resumes = result["hits"]

    total = result.get("estimatedTotalHits", len(resumes))

    return resumes, total


async def search_vacancies(data: SearchVacancies, current_user: User):
    search_options = {
        "limit": data.limit,
        "offset": data.offset
    }

    query_parts = []
    if data.title:
        query_parts.append(data.title.strip())

    if data.city:
        query_parts.append(data.city.strip())

    query_text = " ".join(query_parts)

    filters = []
    if data.compensation:
        filters.append(f"compensation >= {data.compensation}")

    if filters:
        search_options["filter"] = filters

    result = meili.index("vacancies").search(query_text, search_options)
    vacancies = result["hits"]

    total = result.get("estimatedTotalHits", len(vacancies))

    return vacancies, total