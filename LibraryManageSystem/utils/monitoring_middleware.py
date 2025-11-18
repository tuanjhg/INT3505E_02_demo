"""
Monitoring middleware for Flask with Prometheus integration
Tracks request metrics using prometheus_client
"""

import time
from flask import request, g
from utils.metrics_collector import prometheus_metrics
from utils.logger import get_logger

logger = get_logger('monitoring')


def before_request():
    """Store request start time"""
    g.request_start_time = time.time()


def after_request(response):
    """Record Prometheus metrics after request completes"""
    
    # Calculate response time
    if hasattr(g, 'request_start_time'):
        duration_seconds = time.time() - g.request_start_time
    else:
        duration_seconds = 0
    
    # Skip metrics for certain paths
    skip_paths = ['/health', '/metrics', '/static', '/favicon.ico']
    if not any(request.path.startswith(path) for path in skip_paths):
        # Record Prometheus metrics
        prometheus_metrics.record_request(
            method=request.method,
            endpoint=request.path,
            status_code=response.status_code,
            duration=duration_seconds
        )
        
        # Log if response is an error
        response_time_ms = duration_seconds * 1000
        if response.status_code >= 500:
            logger.error(
                f"Server error: {request.method} {request.path} - {response.status_code}",
                extra={
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'response_time_ms': response_time_ms,
                    'request_id': getattr(g, 'request_id', 'unknown')
                }
            )
        elif response.status_code >= 400:
            logger.warning(
                f"Client error: {request.method} {request.path} - {response.status_code}",
                extra={
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'response_time_ms': response_time_ms,
                    'request_id': getattr(g, 'request_id', 'unknown')
                }
            )
    
    return response


def setup_monitoring(app):
    """Setup monitoring middleware for Flask app"""
    app.before_request(before_request)
    app.after_request(after_request)
    
    logger.info("Prometheus monitoring middleware initialized")
