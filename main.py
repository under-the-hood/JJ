from fastapi import FastAPI
import uvicorn

from backend.router import main_router
from backend.database.database import engine


app = FastAPI()

app.include_router(main_router)

if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=8000)