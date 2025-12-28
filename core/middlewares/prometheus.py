from time import time
from typing import Callable

from fastapi import Request, Response
from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


# Define Prometheus metrics
REQUEST_COUNT = Counter(
    "fastapi_requests_total",
    "Total count of requests by method, endpoint and status",
    ["method", "endpoint", "status_code"]
)

REQUEST_DURATION = Histogram(
    "fastapi_request_duration_seconds",
    "Duration of requests by method and endpoint",
    ["method", "endpoint"]
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    Custom Prometheus middleware to track request metrics.
    Tracks request count and duration for all endpoints.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip metrics collection for the metrics endpoint itself
        if request.url.path == "/metrics":
            return await call_next(request)

        # Start timer
        start_time = time()
        
        # Get endpoint path template (e.g., /users/{id} instead of /users/123)
        endpoint = request.url.path
        method = request.method

        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time() - start_time
        
        # Record metrics
        REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status_code=response.status_code
        ).inc()
        
        REQUEST_DURATION.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
        
        return response
