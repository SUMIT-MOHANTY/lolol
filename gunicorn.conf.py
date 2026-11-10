"""
Gunicorn Production Configuration
https://docs.gunicorn.org/en/stable/configure.html

This configuration is optimized for the Django Calculator application
running in containerized production environments.
"""

import multiprocessing
import os

# Server socket binding
bind = os.environ.get("GUNICORN_BIND", "0.0.0.0:8000")

# Worker processes - auto-detect based on CPU cores
# Formula: (2 * CPU cores) + 1 is the Gunicorn recommended default
workers = int(os.environ.get("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))

# Worker class - 'sync' is recommended for CPU-bound Django applications
worker_class = os.environ.get("GUNICORN_WORKER_CLASS", "sync")

# Worker connections (for async workers)
worker_connections = int(os.environ.get("GUNICORN_WORKER_CONNECTIONS", 1000))

# Maximum number of pending connections
backlog = int(os.environ.get("GUNICORN_BACKLOG", 2048))

# Timeout settings (seconds)
timeout = int(os.environ.get("GUNICORN_TIMEOUT", 30))
keepalive = int(os.environ.get("GUNICORN_KEEPALIVE", 2))
graceful_timeout = int(os.environ.get("GUNICORN_GRACEFUL_TIMEOUT", 30))

# Limit request line and header field size for security
limit_request_line = int(os.environ.get("GUNICORN_LIMIT_REQUEST_LINE", 4094))
limit_request_fields = int(os.environ.get("GUNICORN_LIMIT_REQUEST_FIELDS", 100))
limit_request_field_size = int(os.environ.get("GUNICORN_LIMIT_REQUEST_FIELD_SIZE", 8190))

# Logging configuration
accesslog = os.environ.get("GUNICORN_ACCESS_LOG", "-")  # "-" means stdout
errorlog = os.environ.get("GUNICORN_ERROR_LOG", "-")    # "-" means stderr
loglevel = os.environ.get("GUNICORN_LOG_LEVEL", "info")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = os.environ.get("GUNICORN_PROC_NAME", "django_calculator")

# Server mechanics
daemon = False
pidfile = os.environ.get("GUNICORN_PIDFILE", None)

# SSL configuration (when running behind reverse proxy, these are typically not needed)
forwarded_allow_ips = os.environ.get("GUNICORN_FORWARDED_ALLOW_IPS", "*")
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}

# Output capture for Django print statements
capture_output = True
enable_stdio_inheritance = True

# Preload application for memory efficiency
preload_app = True

# Worker temporary directory
worker_tmp_dir = os.environ.get("GUNICORN_WORKER_TMP_DIR", "/dev/shm")


def on_starting(server):
    """Called just before the master process is initialized."""
    pass


def on_reload(server):
    """Called when receiving SIGHUP signal."""
    pass


def when_ready(server):
    """Called just after the server is started."""
    pass


def worker_int(worker):
    """Called when a worker receives SIGINT or SIGQUIT."""
    pass


def worker_abort(worker):
    """Called when a worker receives SIGABRT."""
    pass
