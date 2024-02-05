import functools
from typing import Tuple

import time
from prometheus_client import Counter, Gauge, Histogram
from starlette.requests import Request
from starlette.routing import Match
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from starlette.types import ASGIApp, Message, Receive, Scope, Send

REQUESTS = Counter(
    "starlette_requests_total", "Total count of requests by method and path.", ["method", "path_template"]
)
RESPONSES = Counter(
    "starlette_responses_total",
    "Total count of responses by method, path and status codes.",
    ["method", "path_template", "status_code"],
)
REQUESTS_PROCESSING_TIME = Histogram(
    "starlette_requests_processing_time_seconds",
    "Histogram of requests processing time by path (in seconds)",
    ["method", "path_template"],
)
EXCEPTIONS = Counter(
    "starlette_exceptions_total",
    "Total count of exceptions raised by path and exception type",
    ["method", "path_template", "exception_type"],
)
REQUESTS_IN_PROGRESS = Gauge(
    "starlette_requests_in_progress",
    "Gauge of requests by method and path currently being processed",
    ["method", "path_template"],
    multiprocess_mode='livesum'
)


class PrometheusMiddleware:
    def __init__(self, app: ASGIApp, filter_unhandled_paths: bool = False) -> None:
        self.app = app
        self.filter_unhandled_paths = filter_unhandled_paths

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":  # pragma: no cover
            await self.app(scope, receive, send)
            return

        request = Request(scope)
        method = request.method
        path_template, is_handled_path = self.get_path_template(request)

        if self._is_path_filtered(is_handled_path):
            await self.app(scope, receive, send)
            return

        REQUESTS_IN_PROGRESS.labels(method=method, path_template=path_template).inc()
        REQUESTS.labels(method=method, path_template=path_template).inc()
        before_time = time.perf_counter()

        send = functools.partial(
            self.send, send=send, scope=scope, path_template=path_template, before_time=before_time
        )
        try:
            await self.app(scope, receive, send)
        except BaseException as e:
            EXCEPTIONS.labels(method=method, path_template=path_template, exception_type=type(e).__name__).inc()
            self.write_response_metrics(method, path_template, HTTP_500_INTERNAL_SERVER_ERROR, before_time)
            raise

    async def send(self, message: Message, send: Send, scope: Scope, *, path_template: str, before_time: float) -> None:
        message_type = message["type"]
        if message_type == "http.response.start":
            request = Request(scope)
            method = request.method
            status_code = message["status"]
            self.write_response_metrics(method, path_template, status_code, before_time)

        await send(message)

    def write_response_metrics(self, method: str, path_template: str, status_code: int, before_time: float) -> None:
        after_time = time.perf_counter()
        REQUESTS_PROCESSING_TIME.labels(method=method, path_template=path_template).observe(after_time - before_time)
        RESPONSES.labels(method=method, path_template=path_template, status_code=status_code).inc()
        REQUESTS_IN_PROGRESS.labels(method=method, path_template=path_template).dec()

    @staticmethod
    def get_path_template(request: Request) -> Tuple[str, bool]:
        for route in request.app.routes:
            match, child_scope = route.matches(request.scope)
            if match == Match.FULL:
                return route.path, True

        return request.url.path, False

    def _is_path_filtered(self, is_handled_path: bool) -> bool:
        return self.filter_unhandled_paths and not is_handled_path
