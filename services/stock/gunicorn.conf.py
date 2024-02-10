import multiprocessing

# Bind to 0.0.0.0:8001 (accept connections from outside the container)
bind = "0.0.0.0:8001"

# Number of workers based on available CPUs in the container
workers = multiprocessing.cpu_count() * 2 + 1

# Worker class selection based on application type (asynchronous or not)
worker_class = "gthread"  # Or 'gevent' for asynchronous applications

# Threads per worker for I/O intensive operations
threads = 4

# Timeout for requests
timeout = 30

# Worker temporary directory for better performance
worker_tmp_dir = "/dev/shm"

# Log for access and error
logconfig_dict = {
    "version": 1,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d",
        },
    },
    "handlers": {
        "access": {
            "class": "logging.FileHandler",
            "filename": "/var/log/gunicorn/access.log",
            "formatter": "json",
        },
        "error": {
            "class": "logging.FileHandler",
            "filename": "/var/log/gunicorn/error.log",
            "formatter": "json",
        },
    },
    "root": {"level": "INFO", "handlers": []},
    "loggers": {
        "gunicorn.access": {
            "level": "INFO",
            "handlers": ["access"],
            "propagate": False,
        },
        "gunicorn.error": {
            "level": "INFO",
            "handlers": ["error"],
            "propagate": False,
        },
    },
}
