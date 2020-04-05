import logging.config

import pytest
from sqlalchemy import create_engine

from common.database import create_db, drop_db, apply_migrations, load_data
from common.jwt import get_token
from config import get_config
from main import init_app
from middleware import init_middleware, db_session_middleware
from tests.mock.middleware import db_session_middleware_mock


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
            [
                'user.json', 'tv_show.json', 'episode.json',
                'tracked_tv_show.json', 'user_episode.json',
                'source_info.json', 'source.json',
            ]
        )
        tx.commit()

    yield

    drop_db(config.DATABASE_DEFAULT_URI, config.DB_NAME)


@pytest.yield_fixture
async def app(loop):
    """
    Инициализирует aiohttp приложение и реализует удаление из БД данных
    записанных туда во время теста
    :return: экземпляр инициализированного aiohttp приложения
    """
    def modify_middleware(middlewares):
        index_db_session_middleware = middlewares.index(db_session_middleware)
        middlewares[index_db_session_middleware] = db_session_middleware_mock
        return middlewares

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
async def db_session(app):
    return app['db_session']


@pytest.fixture
async def client(app, aiohttp_client):
    """
    Инициализирует клиент позволяющий выполнять HTTP запросы к
    разрабатываемому приложению
    """
    return await aiohttp_client(app)


@pytest.fixture
def token_user1():
    return get_token(1)


@pytest.fixture
def headers_user1(token_user1):
    return {
        'Authorization': f'Bearer {token_user1}'
    }


@pytest.fixture
def token_user2():
    return get_token(2)


@pytest.fixture
def headers_user2(token_user2):
    return {
        'Authorization': f'Bearer {token_user2}'
    }
