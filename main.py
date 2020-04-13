import asyncio
import logging.config

from aiohttp import web

from auth.routes import init_routes as auth_init_routes
from config import get_config
from db import init_db, close_db
from middleware import init_middleware
from scheduler import init_scheduler, shutdown_scheduler
from tv_show.routes import init_routes as tv_show_init_routes


async def init_app(config, middleware) -> web.Application:
    app = web.Application(middlewares=middleware)
    app['config'] = config
    auth_init_routes(app)
    tv_show_init_routes(app)
    app.on_startup.append(init_db)
    app.on_startup.append(init_scheduler)
    app.on_cleanup.append(close_db)
    app.on_cleanup.append(shutdown_scheduler)
    return app


async def app_factory() -> web.Application:
    config = get_config()
    logging.config.dictConfig(config.LOGGING_CONFIG)
    asyncio.get_event_loop().set_debug(config.IS_DEBUG)

    middleware = init_middleware(config)

    return await init_app(config, middleware)


def run():
    config = get_config()
    app = app_factory()
    web.run_app(app, host=config.HOST, port=config.PORT)


if __name__ == '__main__':
    run()
