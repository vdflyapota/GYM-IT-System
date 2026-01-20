from flask import request
from prometheus_client import Counter

http_request_counter = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)

def register_custom_metrics(app):
    @app.after_request
    def after_request(response):
        try:
            http_request_counter.labels(
                request.method, request.path, response.status_code
            ).inc()
        except Exception:
            pass
        return response
