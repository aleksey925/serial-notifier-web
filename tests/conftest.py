import logging.config

import pytest
from sqlalchemy import create_engine

from config import get_config
from main import init_app
from middleware import init_middleware
from tests.utils.db import create_db, drop_db, apply_migrations, load_data
from tests.utils.middleware import modify_middleware


@pytest.yield_fixture(scope='session', autouse=True)
def init_test_db():
    """
    Выполняет инициализацию тестовой БД
    """
    config = get_config()

    create_db(config.DATABASE_DEFAULT_URI, config.DB_NAME)
    apply_migrations(config.BASE_DIR)

    with create_engine(config.DATABASE_URI).connect() as db_session:
        tx = db_session.begin()
        load_data(
            db_session,
            config.FIXTURES_PATH,
            ['test_user.json', 'test_tv_show.json', 'test_episode.json']
        )
        tx.commit()

    yield

    drop_db(config.DATABASE_DEFAULT_URI, config.DB_NAME)


@pytest.yield_fixture
async def app():
    """
    Инициализирует aiohttp приложение и реализует удаление из БД данных
    записанных туда во время теста
    :return: экземпляр инициализированного aiohttp приложения
    """
    config = get_config()
    logging.config.dictConfig(config.LOGGING_CONFIG)
    middleware = modify_middleware(init_middleware(config))

    web_app = await init_app(config, middleware)

    async with web_app['db_pool'].acquire() as db_session:
        web_app['db_session'] = db_session
        tx = db_session.transaction()
        await tx.start()

        yield web_app

        await tx.rollback()


@pytest.fixture
def db_session(app):
    return app['db_session']


@pytest.fixture
async def client(app, aiohttp_client):
    """
    Инициализирует клиент позволяющий выполнять HTTP запросы к
    разрабатываемому приложению
    """
    return await aiohttp_client(app)
