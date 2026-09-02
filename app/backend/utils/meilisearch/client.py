import meilisearch
from app.backend.config import settings

meili = meilisearch.Client(f"http://{settings.MEILI_HTTP_ADDR}:7700", settings.MEILI_MASTER_KEY)