import os

from prometheus_client import CollectorRegistry, CONTENT_TYPE_LATEST, REGISTRY, generate_latest
from prometheus_client.multiprocess import MultiProcessCollector
from starlette.requests import Request
from starlette.responses import Response


def metrics(request: Request) -> Response:
    if "prometheus_multiproc_dir" in os.environ:
        registry = CollectorRegistry()
        MultiProcessCollector(registry)
    else:
        registry = REGISTRY

    return Response(generate_latest(registry), media_type=CONTENT_TYPE_LATEST)
