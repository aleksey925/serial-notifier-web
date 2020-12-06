import pytest
from aiohttp.test_utils import TestClient
from httpx import AsyncClient
from sqlalchemy import create_engine

from auth.security import create_access_token
from common.database import create_db, drop_db, apply_migrations, load_data
from config import get_config
from db import close_db, init_db, get_db
from main import app_factory


@pytest.yield_fixture(scope='session', autouse=True)
def init_test_db():
    """
    Выполняет инициализацию тестовой БД
    """
    config = get_config()

    create_db(config.DATABASE_DEFAULT_URI, config.DB_NAME)
    apply_migrations(config.BASE_DIR)

    with create_engine(config.DATABASE_URI.replace('+aiopg', '')).connect() as db_session:
        tx = db_session.begin()
        load_data(
            db_session,
            config.FIXTURES_PATH,
            [
                'user.json', 'tv_show.json', 'episode.json',
                'tracked_tv_show.json', 'user_episode.json',
                'source_info.json', 'source.json', 'telegram_acc.json',
            ]
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
    application = app_factory(app_event=lambda *args, **kwargs: None)
    await init_db()

    yield application

    await close_db()


@pytest.fixture
async def db_session(app):
    return get_db()


@pytest.fixture
def client(app, aiohttp_client):
    """
    Инициализирует клиент позволяющий выполнять HTTP запросы к
    разрабатываемому приложению
    """
    return TestClient(app)


@pytest.yield_fixture
async def async_client(app):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def token_user1():
    return create_access_token({'user_id': 1})


@pytest.fixture
def headers_user1(token_user1):
    return {
        'Authorization': f'Bearer {token_user1}'
    }


@pytest.fixture
def token_user2():
    return create_access_token({'user_id': 2})


@pytest.fixture
def headers_user2(token_user2):
    return {
        'Authorization': f'Bearer {token_user2}'
    }
