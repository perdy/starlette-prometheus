# Starlette Prometheus
[![Build Status](https://github.com/perdy/starlette-prometheus/workflows/Continuous%20Integration/badge.svg)](https://github.com/perdy/starlette-prometheus/actions)
[![codecov](https://codecov.io/gh/perdy/starlette-prometheus/branch/master/graph/badge.svg)](https://codecov.io/gh/perdy/starlette-prometheus)
[![Package Version](https://img.shields.io/pypi/v/starlette-prometheus?logo=PyPI&logoColor=white)](https://pypi.org/project/starlette-prometheus/)
[![PyPI Version](https://img.shields.io/pypi/pyversions/starlette-prometheus?logo=Python&logoColor=white)](https://pypi.org/project/starlette-prometheus/)

## Introduction

Prometheus integration for Starlette.

## Requirements

* Python 3.6+
* Starlette 0.9+

## Installation

```console
$ pip install starlette-prometheus
```

## Usage

A complete example that exposes prometheus metrics endpoint under `/metrics/` path.

```python
from starlette.applications import Starlette
from starlette_prometheus import metrics, PrometheusMiddleware

app = Starlette()

app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics/", metrics)
```

Metrics for paths that do not match any Starlette route can be filtered by passing
`filter_unhandled_paths=True` argument to `add_middleware` method.

## Contributing

This project is absolutely open to contributions so if you have a nice idea, create an issue to let the community 
discuss it.
