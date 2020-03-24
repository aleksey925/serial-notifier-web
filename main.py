import asyncio
import logging.config

from aiohttp import web

from auth.routes import init_routes as auth_init_routes
from tv_show.routes import init_routes as tv_show_init_routes
from config import get_config
from db import init_db
from middleware import init_middleware


async def init_app(config, middleware) -> web.Application:
    app = web.Application(middlewares=middleware)
    app['config'] = config
    auth_init_routes(app)
    tv_show_init_routes(app)
    await init_db(app)
    return app


def main():
    config = get_config()
    logging.config.dictConfig(config.LOGGING_CONFIG)
    asyncio.get_event_loop().set_debug(config.IS_DEBUG)

    middleware = init_middleware(config)

    app = init_app(config, middleware)
    web.run_app(app, host=config.HOST, port=config.PORT)


if __name__ == '__main__':
    main()
