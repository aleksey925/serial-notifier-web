import os

host = '0.0.0.0'
port = os.getenv('APP_PORT', '80')

# Gunicorn config variables
bind = f'{host}:{port}'
workers = int(os.getenv('COUNT_WORKERS', '4'))
worker_class = 'uvicorn.workers.UvicornWorker'
worker_tmp_dir = '/dev/shm'
graceful_timeout = int(os.getenv('GRACEFUL_TIMEOUT', '120'))
timeout = int(os.getenv('TIMEOUT', '120'))
keepalive = int(os.getenv('KEEP_ALIVE', '5'))
