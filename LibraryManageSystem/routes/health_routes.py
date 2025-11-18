"""
Health check and metrics endpoints for monitoring
Provides liveness, readiness probes and Prometheus metrics
"""

from flask import Blueprint, jsonify
from datetime import datetime
import time
import os
import psutil
from models import db
from utils.metrics_collector import prometheus_metrics

health_bp = Blueprint('health', __name__)

# Store app start time
START_TIME = time.time()


def check_database():
    """Check if database connection is healthy"""
    try:
        # Simple query to verify connection
        db.session.execute(db.text('SELECT 1'))
        return {'status': 'healthy', 'message': 'Database connection OK'}
    except Exception as e:
        return {'status': 'unhealthy', 'message': f'Database error: {str(e)}'}


def check_redis():
    """Check if Redis connection is healthy (for rate limiting)"""
    try:
        from utils.rate_limiter import limiter
        if hasattr(limiter, 'storage'):
            # Try to perform a simple operation
            storage = limiter.storage
            if storage:
                return {'status': 'healthy', 'message': 'Redis connection OK'}
        return {'status': 'healthy', 'message': 'Redis not configured (using memory storage)'}
    except Exception as e:
        return {'status': 'degraded', 'message': f'Redis warning: {str(e)}'}


def check_disk_space():
    """Check available disk space"""
    try:
        disk = psutil.disk_usage('/')
        percent_used = disk.percent
        
        if percent_used > 90:
            return {
                'status': 'critical',
                'message': f'Disk space critically low: {percent_used}% used',
                'percent_used': percent_used
            }
        elif percent_used > 80:
            return {
                'status': 'warning',
                'message': f'Disk space getting low: {percent_used}% used',
                'percent_used': percent_used
            }
        else:
            return {
                'status': 'healthy',
                'message': f'Disk space OK: {percent_used}% used',
                'percent_used': percent_used
            }
    except Exception as e:
        return {'status': 'unknown', 'message': f'Could not check disk: {str(e)}'}


def get_system_stats():
    """Get system resource statistics"""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_available_mb': memory.available / (1024 * 1024),
            'memory_total_mb': memory.total / (1024 * 1024)
        }
    except Exception as e:
        return {'error': str(e)}


@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Basic health check - liveness probe
    Returns 200 if application is running
    """
    uptime_seconds = int(time.time() - START_TIME)
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'service': 'Library Management API',
        'version': os.getenv('API_VERSION', '2.0.0'),
        'uptime_seconds': uptime_seconds
    }), 200


@health_bp.route('/health/ready', methods=['GET'])
def readiness_check():
    """
    Readiness check - checks if app can serve traffic
    Verifies database and critical dependencies
    """
    checks = {
        'database': check_database(),
        'redis': check_redis(),
        'disk': check_disk_space()
    }
    
    # Determine overall status
    all_healthy = all(
        check['status'] in ['healthy', 'degraded']
        for check in checks.values()
    )
    
    overall_status = 'ready' if all_healthy else 'not_ready'
    status_code = 200 if all_healthy else 503
    
    uptime_seconds = int(time.time() - START_TIME)
    
    response = {
        'status': overall_status,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'version': os.getenv('API_VERSION', '2.0.0'),
        'uptime_seconds': uptime_seconds,
        'checks': checks
    }
    
    return jsonify(response), status_code


@health_bp.route('/health/live', methods=['GET'])
def liveness_check():
    """
    Kubernetes-style liveness probe
    Returns 200 if process is alive
    """
    return jsonify({
        'status': 'alive',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }), 200


@health_bp.route('/metrics', methods=['GET'])
def metrics():
    """
    Expose Prometheus metrics
    Returns metrics in Prometheus exposition format
    """
    # Return Prometheus metrics
    return prometheus_metrics.get_metrics_response()


@health_bp.route('/health/detailed', methods=['GET'])
def detailed_health():
    """
    Detailed health information including metrics
    For admin/debugging purposes
    """
    checks = {
        'database': check_database(),
        'redis': check_redis(),
        'disk': check_disk_space()
    }
    
    system_stats = get_system_stats()
    uptime = int(time.time() - START_TIME)
    
    all_healthy = all(
        check['status'] in ['healthy', 'degraded']
        for check in checks.values()
    )
    
    return jsonify({
        'status': 'healthy' if all_healthy else 'degraded',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'version': os.getenv('API_VERSION', '2.0.0'),
        'environment': os.getenv('ENVIRONMENT', 'development'),
        'uptime_seconds': uptime,
        'health_checks': checks,
        'system_metrics': system_stats,
        'note': 'For detailed metrics, see /metrics endpoint (Prometheus format)'
    }), 200 if all_healthy else 503
