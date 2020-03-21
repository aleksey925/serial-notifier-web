from aiohttp import web
from aiohttp_jwt import JWTMiddleware


@web.middleware
async def db_session_middleware(request, handler):
    async with request.app['db_pool'].acquire() as db_session:
        request['db_session'] = db_session
        return await handler(request)


def init_middleware(config):
    middlewares = [
        db_session_middleware,
        JWTMiddleware(config.JWT_SECRET, credentials_required=False),
    ]

    return middlewares
