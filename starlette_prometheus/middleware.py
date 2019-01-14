import time

from prometheus_client import Counter, Gauge, Histogram
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.types import ASGIInstance

REQUESTS = Counter("starlette_requests_total", "Total count of requests by mathod and path.", ["method", "path"])
RESPONSES = Counter(
    "starlette_responses_total",
    "Total count of responses by method, path and status codes.",
    ["method", "path", "status_code"],
)
REQUESTS_PROCESSING_TIME = Histogram(
    "starlette_requests_processing_time_seconds",
    "Histogram of requests processing time by path (in seconds)",
    ["method", "path"],
)
EXCEPTIONS = Counter(
    "starlette_exceptions_total",
    "Histogram of exceptions raised by path and exception type",
    ["method", "path", "exception_type"],
)
REQUESTS_IN_PROGRESS = Gauge("starlette_requests_in_progress", "Gauge of requests currently being processed")


class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> ASGIInstance:
        method = request.method
        path = request.url.path

        REQUESTS_IN_PROGRESS.inc()
        REQUESTS.labels(method=method, path=path).inc()
        try:
            before_time = time.time()
            response = await call_next(request)
            after_time = time.time()
        except Exception as e:
            EXCEPTIONS.labels(method=method, path=path, exception_type=type(e).__name__).inc()
            raise e from None
        else:
            REQUESTS_PROCESSING_TIME.labels(method=method, path=path).observe(after_time - before_time)
            RESPONSES.labels(method=method, path=path, status_code=response.status_code).inc()
        finally:
            REQUESTS_IN_PROGRESS.dec()

        return response
