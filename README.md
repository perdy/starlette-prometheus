# Starlette Prometheus
[![Build Status](https://travis-ci.org/PeRDy/starlette-prometheus.svg?branch=master)](https://travis-ci.org/PeRDy/starlette-prometheus)
[![codecov](https://codecov.io/gh/PeRDy/starlette-prometheus/branch/master/graph/badge.svg)](https://codecov.io/gh/PeRDy/starlette-prometheus)
[![PyPI version](https://badge.fury.io/py/starlette-prometheus.svg)](https://badge.fury.io/py/starlette-prometheus)

* **Version:** 0.1.0
* **Status:** Production/Stable
* **Author:** José Antonio Perdiguero López

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

## Contributing

This project is absolutely open to contributions so if you have a nice idea, create an issue to let the community 
discuss it.