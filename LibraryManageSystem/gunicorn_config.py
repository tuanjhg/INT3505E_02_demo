# =======================================================================
# Gunicorn Configuration for Production
# =======================================================================

import multiprocessing
import os

# Server Socket
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
backlog = 2048

# Worker Processes
# ✅ Tăng workers cho PostgreSQL (hỗ trợ concurrency tốt hơn SQLite)
cpu_count = multiprocessing.cpu_count()
default_workers = min((2 * cpu_count) + 1, 8)  # Tối đa 8 workers cho PostgreSQL
workers = int(os.getenv('WORKERS', default_workers))
worker_class = os.getenv('WORKER_CLASS', 'sync')
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = int(os.getenv('WORKER_TIMEOUT', '120'))
keepalive = 5

# ✅ Không cần preload cho PostgreSQL
# preload_app = True

# Process Naming
proc_name = 'library-api'

# Logging
accesslog = os.getenv('GUNICORN_ACCESS_LOG', 'logs/gunicorn-access.log')
errorlog = os.getenv('GUNICORN_ERROR_LOG', 'logs/gunicorn-error.log')
loglevel = os.getenv('LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# Server Mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if using Gunicorn for SSL, otherwise use Nginx)
keyfile = os.getenv('SSL_KEY_FILE', None)
certfile = os.getenv('SSL_CERT_FILE', None)

# Hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    print("🚀 Starting Gunicorn server...")

def on_reload(server):
    """Called to recycle workers during a reload."""
    print("♻️  Reloading Gunicorn workers...")

def when_ready(server):
    """Called just after the server is started."""
    print(f"✅ Gunicorn is ready. Listening on {bind}")
    print(f"👷 Workers: {workers} (optimized for PostgreSQL)")
    print(f"⏱️  Timeout: {timeout}s")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    pass

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    print(f"👷 Worker spawned (pid: {worker.pid})")

def pre_exec(server):
    """Called just before a new master process is forked."""
    print("🔄 Forking new master process...")

def worker_int(worker):
    """Called when a worker receives the INT or QUIT signal."""
    print(f"⚠️  Worker received INT/QUIT signal (pid: {worker.pid})")

def worker_abort(worker):
    """Called when a worker receives the SIGABRT signal."""
    print(f"❌ Worker aborted (pid: {worker.pid})")
