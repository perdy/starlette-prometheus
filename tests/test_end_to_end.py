import pytest
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.testclient import TestClient

from starlette_prometheus import PrometheusMiddleware, metrics


class TestCasePrometheusMiddleware:
    @pytest.fixture(scope="class")
    def app(self):
        app_ = Starlette()
        app_.add_middleware(PrometheusMiddleware)
        app_.add_route("/metrics/", metrics)

        @app_.route("/foo/")
        def foo(request):
            return PlainTextResponse("Foo")

        @app_.route("/bar/")
        def bar(request):
            raise ValueError("bar")

        return app_

    @pytest.fixture
    def client(self, app):
        return TestClient(app)

    def test_view_ok(self, client):
        # Do a request
        client.get("/foo/")

        # Get metrics
        response = client.get("/metrics/")
        metrics_text = response.content.decode()

        # Asserts: Requests
        assert 'starlette_requests_total{method="GET",path="/foo/"} 1.0' in metrics_text

        # Asserts: Responses
        assert 'starlette_responses_total{method="GET",path="/foo/",status_code="200"} 1.0' in metrics_text

        # Asserts: Requests in progress
        assert 'starlette_requests_in_progress{method="GET",path="/foo/"} 0.0' in metrics_text
        assert 'starlette_requests_in_progress{method="GET",path="/metrics/"} 1.0' in metrics_text

    def test_view_exception(self, client):
        # Do a request
        with pytest.raises(ValueError):
            client.get("/bar/")

        # Get metrics
        response = client.get("/metrics/")
        metrics_text = response.content.decode()

        # Asserts: Requests
        assert 'starlette_requests_total{method="GET",path="/bar/"} 1.0' in metrics_text

        # Asserts: Responses
        assert 'starlette_exceptions_total{exception_type="ValueError",method="GET",path="/bar/"} 1.0' in metrics_text

        # Asserts: Requests in progress
        assert 'starlette_requests_in_progress{method="GET",path="/bar/"} 0.0' in metrics_text
        assert 'starlette_requests_in_progress{method="GET",path="/metrics/"} 1.0' in metrics_text
