import time
import requests
import meilisearch
from testcontainers.core.container import DockerContainer

import app.backend.utils.meilisearch.client as meili_client 


meili_container = (
    DockerContainer("getmeili/meilisearch:v1.6")
    .with_env("MEILI_MASTER_KEY", "test_meili_key")
    .with_exposed_ports(7700)
)
meili_container.start()

meili_host = meili_container.get_container_host_ip()
meili_port = meili_container.get_exposed_port(7700)
meili_url = f"http://{meili_host}:{meili_port}"

_deadline = time.time() + 30
while time.time() < _deadline:
    try:
        if requests.get(f"{meili_url}/health", timeout=1).status_code == 200:
            break
    except requests.exceptions.ConnectionError:
        pass
    time.sleep(0.5)
else:
    raise RuntimeError("Meilisearch container didn't become ready in time")

meili_client.meili = meilisearch.Client(meili_url, "test_meili_key")

def stop():
    try:
        meili_container.stop()
    except Exception as e:
        print(f"Failed to stop Meilisearch testcontainer: {e}")