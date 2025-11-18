"""
Prometheus metrics collector for monitoring application performance
Uses prometheus_client for industry-standard metrics export
"""

import time
from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
from flask import Response
import psutil


# Application info
app_info = Info('library_api_info', 'Library Management API Information')
app_info.info({
    'version': '2.0.0',
    'environment': 'production'
})

# Request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint'],
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0)
)

http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'Number of HTTP requests in progress',
    ['method', 'endpoint']
)

http_errors_total = Counter(
    'http_errors_total',
    'Total HTTP errors',
    ['method', 'endpoint', 'status_code']
)

# Database metrics
db_connections_active = Gauge(
    'db_connections_active',
    'Number of active database connections'
)

db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['query_type'],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0)
)

# System metrics
system_cpu_usage = Gauge(
    'system_cpu_usage_percent',
    'System CPU usage percentage'
)

system_memory_usage = Gauge(
    'system_memory_usage_percent',
    'System memory usage percentage'
)

system_memory_available_bytes = Gauge(
    'system_memory_available_bytes',
    'Available system memory in bytes'
)

system_disk_usage = Gauge(
    'system_disk_usage_percent',
    'System disk usage percentage'
)

# Application uptime
app_uptime_seconds = Gauge(
    'app_uptime_seconds',
    'Application uptime in seconds'
)

# Business metrics
books_total = Gauge(
    'books_total',
    'Total number of books in library'
)

books_borrowed = Gauge(
    'books_borrowed',
    'Number of books currently borrowed'
)

users_total = Gauge(
    'users_total',
    'Total number of registered users'
)

# Start time for uptime calculation
START_TIME = time.time()


class PrometheusMetrics:
    """Prometheus metrics collector with helper methods"""
    
    @staticmethod
    def record_request(method: str, endpoint: str, status_code: int, duration: float):
        """
        Record HTTP request metrics
        
        Args:
            method: HTTP method (GET, POST, etc)
            endpoint: Request endpoint/path
            status_code: HTTP status code
            duration: Request duration in seconds
        """
        # Increment request counter
        http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code
        ).inc()
        
        # Record duration
        http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
        
        # Track errors
        if status_code >= 400:
            http_errors_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).inc()
    
    @staticmethod
    def track_request_in_progress(method: str, endpoint: str):
        """Context manager to track requests in progress"""
        class RequestTracker:
            def __enter__(self):
                http_requests_in_progress.labels(method=method, endpoint=endpoint).inc()
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                http_requests_in_progress.labels(method=method, endpoint=endpoint).dec()
        
        return RequestTracker()
    
    @staticmethod
    def update_system_metrics():
        """Update system resource metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            system_cpu_usage.set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            system_memory_usage.set(memory.percent)
            system_memory_available_bytes.set(memory.available)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            system_disk_usage.set(disk.percent)
            
            # Uptime
            uptime = time.time() - START_TIME
            app_uptime_seconds.set(uptime)
        except Exception as e:
            pass  # Silently fail if psutil fails
    
    @staticmethod
    def update_business_metrics():
        """Update business/domain-specific metrics"""
        try:
            from models import db
            from models.book import Book
            from models.borrow import BorrowRecord
            from models.user import User
            
            # Count books
            total_books = db.session.query(Book).count()
            books_total.set(total_books)
            
            # Count borrowed books (not returned)
            borrowed = db.session.query(BorrowRecord).filter_by(returned=False).count()
            books_borrowed.set(borrowed)
            
            # Count users
            total_users = db.session.query(User).count()
            users_total.set(total_users)
        except Exception as e:
            # Silently fail if database is not available or models not imported
            # This prevents metrics endpoint from failing in Docker startup
            pass
    
    @staticmethod
    def get_metrics_response():
        """Generate Prometheus metrics response"""
        # Update system and business metrics before exporting
        PrometheusMetrics.update_system_metrics()
        PrometheusMetrics.update_business_metrics()
        
        # Generate metrics in Prometheus format
        metrics_output = generate_latest()
        return Response(metrics_output, mimetype=CONTENT_TYPE_LATEST)


# Global instance
prometheus_metrics = PrometheusMetrics()


# Backward compatibility wrapper
class MetricsCollector:
    """Backward compatibility wrapper for existing code"""
    
    def record_request(self, endpoint: str, method: str, status_code: int, response_time_ms: float):
        """Record request using Prometheus metrics"""
        duration_seconds = response_time_ms / 1000.0
        prometheus_metrics.record_request(method, endpoint, status_code, duration_seconds)
    
    def get_stats(self) -> dict:
        """Get legacy stats format (for compatibility)"""
        # Return empty dict - use /metrics endpoint instead
        return {
            'total_requests': 0,
            'total_errors': 0,
            'error_rate': 0,
            'avg_response_time_ms': 0,
            'requests_per_second': 0,
            'message': 'Use /metrics endpoint for Prometheus metrics'
        }


# Global instance for backward compatibility
metrics_collector = MetricsCollector()
