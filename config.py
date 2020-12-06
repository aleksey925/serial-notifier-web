import os
from os import path

from dotenv import load_dotenv
from jose.constants import ALGORITHMS


class BaseConfig:
    def __init__(self):
        self.BASE_DIR = path.abspath(path.dirname(__file__))
        self.CURRENT_ENV = os.environ.get('CURRENT_ENV', 'dev')
        self.LOCAL_MODE = bool(int(os.environ.get('LOCAL_MODE', 1)))
        self.LOCAL_HOST = '127.0.0.1'

        # JWT
        self.JWT_SECRET = os.environ['JWT_SECRET']
        self.JWT_EXP_DELTA_MIN = 60
        self.JWT_ALGORITHM = ALGORITHMS.HS256

        # db
        self.DB_HOST = os.environ.get('POSTGRES_HOST', 'db')
        self.DB_PORT = os.environ.get('POSTGRES_PORT', '5432')
        self.DB_USER = os.environ['POSTGRES_USER']
        self.DB_PASSWORD = os.environ['POSTGRES_PASSWORD']
        self.DB_NAME = os.environ['POSTGRES_DB']

        # TELEGRAM BOT
        self.TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')

    @property
    def DATABASE_URI(self):
        return (
            f'postgresql+aiopg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
        )


class DevConfig(BaseConfig):
    def __init__(self):
        super().__init__()

        # db
        self.DB_HOST = self.LOCAL_HOST if self.LOCAL_MODE else self.DB_HOST


class TestConfig(DevConfig):
    def __init__(self):
        super().__init__()

        # db
        self.DB_NAME = f'test_{self.DB_NAME}'
        self.DB_NAME_DEFAULT = 'postgres'

        # test data
        self.FIXTURES_PATH = path.join(self.BASE_DIR, 'tests', 'fixtures')

    @property
    def DATABASE_URI(self):
        return (
            f'postgresql+aiopg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
        )

    @property
    def DATABASE_DEFAULT_URI(self):
        return (
            f'postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME_DEFAULT}'
        )


class ProdConfig(BaseConfig):
    def __init__(self):
        super().__init__()


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
