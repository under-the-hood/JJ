from fastapi import FastAPI, Response
import prometheus_client
from prometheus_fastapi_instrumentator import Instrumentator


def setup_metrics(app: FastAPI):
    Instrumentator().instrument(app)

    @app.get("/metrics", tags=["Metrics"])
    def get_metrics():
        return Response(
            content=prometheus_client.generate_latest(),
            media_type="text/plain",
        )