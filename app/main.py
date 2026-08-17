from fastapi import FastAPI
import uvicorn

from app.backend.router import main_router
from app.backend.core.metrics import setup_metrics
from app.backend.utils.search import init_meilisearch


app = FastAPI(root_path="/api")

setup_metrics(app)
init_meilisearch()
app.include_router(main_router)

if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=8000)