import pytest
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.testclient import TestClient

from starlette_prometheus import metrics, PrometheusMiddleware

app = Starlette()
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics/", metrics)


@app.route("/foo/")
def foo(request):
    return PlainTextResponse("Foo")


@app.route("/bar/")
def bar(request):
    raise ValueError("bar")


@pytest.fixture
def client():
    return TestClient(app)


class TestCasePrometheusMiddleware:
    def test_view_ok(self, client):
        # Do a request
        client.get("/foo/")

        # Get metrics
        response = client.get("/metrics/")
        metrics_text = response.content.decode()

        # Asserts
        assert 'starlette_requests_total{method="GET",path="/foo/"} 1.0' in metrics_text
        assert 'starlette_responses_total{method="GET",path="/foo/",status_code="200"} 1.0' in metrics_text
        assert 'starlette_requests_in_progress 1.0' in metrics_text  # metrics call is in progress when got the response

    def test_view_exception(self, client):
        # Do a request
        with pytest.raises(ValueError):
            client.get("/bar/")

        # Get metrics
        response = client.get("/metrics/")
        metrics_text = response.content.decode()

        # Asserts
        assert 'starlette_requests_total{method="GET",path="/bar/"} 1.0' in metrics_text
        assert 'starlette_exceptions_total{exception_type="ValueError",method="GET",path="/bar/"} 1.0' in metrics_text
        assert 'starlette_requests_in_progress 1.0' in metrics_text  # metrics call is in progress when got the response
