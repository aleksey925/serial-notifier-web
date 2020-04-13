from config import get_config

_config = get_config()

user = 'application'
group = 'application'

bind = f'{_config.HOST}:{_config.PORT}'
workers = _config.COUNT_WORKERS
reload = _config.GUNICORN_RELOAD
preload_app = True
worker_class = 'aiohttp.worker.GunicornUVLoopWebWorker'
