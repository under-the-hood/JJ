from fastapi import FastAPI
import uvicorn

from app.backend.router import main_router
from app.backend.core.metrics import setup_metrics


app = FastAPI(root_path="/api")

setup_metrics(app)
app.include_router(main_router)

if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=8000)