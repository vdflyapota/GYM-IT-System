from flask import request, Response
import requests
from .config import Config

# Service routing configuration
SERVICE_ROUTES = {
    "/api/auth": Config.AUTH_SERVICE_URL,
    "/api/users": Config.USER_SERVICE_URL,
    "/api/tournaments": Config.TOURNAMENT_SERVICE_URL,
    "/api/notifications": Config.NOTIFICATION_SERVICE_URL,
}

def get_target_service(path):
    """Determine which service to route to based on request path"""
    for prefix, service_url in SERVICE_ROUTES.items():
        if path.startswith(prefix):
            return service_url, path
    return None, path

def proxy_request(service_url, path):
    """Proxy the request to the target service"""
    if not service_url:
        return {"error": "Service not found"}, 404
    
    # Build target URL
    target_url = f"{service_url}{path}"
    
    # Get request data
    headers = {key: value for key, value in request.headers if key.lower() != 'host'}
    data = request.get_data()
    params = request.args
    
    try:
        # Forward the request
        response = requests.request(
            method=request.method,
            url=target_url,
            headers=headers,
            data=data,
            params=params,
            allow_redirects=False,
            timeout=30
        )
        
        # Build response
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        response_headers = [
            (name, value) for name, value in response.headers.items()
            if name.lower() not in excluded_headers
        ]
        
        return Response(
            response.content,
            response.status_code,
            response_headers
        )
    except requests.exceptions.RequestException as e:
        return {"error": f"Service unavailable: {str(e)}"}, 503
