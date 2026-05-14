from fastapi import FastAPI, Response
import uvicorn
from prometheus_fastapi_instrumentator import Instrumentator
import prometheus_client

from app.backend.router import main_router


app = FastAPI(root_path="/api")

@app.get("/metrics")
def get_metrics():
    return Response(
        content=prometheus_client.generate_latest(), 
        media_type="text/plain"
    )

app.include_router(main_router)
instrumentator = Instrumentator().instrument(app)

if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=8000)