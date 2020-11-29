import multiprocessing
import os
from copy import deepcopy
from os import path

from dotenv import load_dotenv

_LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': {
        # root logger
        '': {
            'handlers': ['default'],
            'level': 'WARNING',
            'propagate': False
        },
    }
}


def _init_logging_config(level: str):
    logging_conf = deepcopy(_LOGGING_CONFIG)
    logging_conf['handlers']['default']['level'] = level
    logging_conf['loggers']['']['level'] = level
    return logging_conf


class BaseConfig:
    def __init__(self):
        self.BASE_DIR = path.abspath(path.dirname(__file__))
        self.CURRENT_ENV = os.environ.get('CURRENT_ENV', 'dev')
        self.LOCAL_MODE = bool(int(os.environ.get('LOCAL_MODE', 1)))
        self.LOCAL_HOST = '127.0.0.1'

        self.LOGGER_LEVEL = 'INFO'
        self.LOGGING_CONFIG = _init_logging_config(self.LOGGER_LEVEL)

        # aiohttp
        self.HOST = '0.0.0.0'
        self.PORT = 8080
        self.IS_DEBUG = False

        # JWT
        self.JWT_SECRET = os.environ['JWT_SECRET']
        self.JWT_EXP_DELTA_MIN = 60
        self.JWT_ALGORITHM = 'HS256'

        # db
        self.DB_HOST = 'db'
        self.DB_PORT = '5432'
        self.DB_USER = os.environ['POSTGRES_USER']
        self.DB_PASSWORD = os.environ['POSTGRES_PASSWORD']
        self.DB_NAME = os.environ['POSTGRES_DB']

        # TELEGRAM BOT
        self.TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')

    @property
    def DATABASE_URI(self):
        return (
            f'postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
        )


class DevConfig(BaseConfig):
    def __init__(self):
        super().__init__()

        self.LOGGER_LEVEL = 'DEBUG'
        self.LOGGING_CONFIG = _init_logging_config(self.LOGGER_LEVEL)

        # aiohttp
        self.DEBUG = True

        # db
        self.DB_HOST = self.LOCAL_HOST if self.LOCAL_MODE else self.DB_HOST


class TestConfig(DevConfig):
    def __init__(self):
        super().__init__()

        self.LOGGER_LEVEL = 'DEBUG'
        self.LOGGING_CONFIG = _init_logging_config(self.LOGGER_LEVEL)

        # db
        self.DB_NAME = f'test_{self.DB_NAME}'
        self.DB_NAME_DEFAULT = 'postgres'

        # test data
        self.FIXTURES_PATH = path.join(self.BASE_DIR, 'tests', 'fixtures')

    @property
    def DATABASE_URI(self):
        return (
            f'postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
        )

    @property
    def DATABASE_DEFAULT_URI(self):
        return (
            f'postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME_DEFAULT}'
        )


class ProdConfig(BaseConfig):
    def __init__(self):
        super().__init__()

        self.COUNT_WORKERS = multiprocessing.cpu_count() * 2 + 1
        self.GUNICORN_RELOAD = False


config = {
    'dev': DevConfig,
    'test': TestConfig,
    'prod': ProdConfig
}


def _get_config_gen():
    load_dotenv()
    conf = config[os.environ.get('CURRENT_ENV', 'dev')]()
    while True:
        yield conf


_config_gen = _get_config_gen()
next(_config_gen)


def get_config():
    return next(_config_gen)
