import os
from pathlib import Path

from dotenv import load_dotenv
from jose.constants import ALGORITHMS


class BaseConfig:
    def __init__(self):
        self.BASE_DIR = Path(__file__).parent
        self.CURRENT_ENV = os.environ.get('CURRENT_ENV', 'dev')
        self.LOCAL_MODE = bool(int(os.environ.get('LOCAL_MODE', 1)))

        # SERIAL-NOTIFIER
        self.API_BASE_URL = os.environ['API_BASE_URL']

        # JWT
        self.JWT_SECRET = os.environ['JWT_SECRET']
        self.JWT_EXP_DELTA_MIN = int(os.environ.get('JWT_EXP_DELTA_MIN', '60'))
        self.JWT_ALGORITHM = getattr(ALGORITHMS, os.environ['JWT_ALGORITHM'])

        # TELEGRAM BOT
        self.TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')


class DevConfig(BaseConfig):
    def __init__(self):
        super().__init__()


class TestConfig(DevConfig):
    def __init__(self):
        super().__init__()


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
