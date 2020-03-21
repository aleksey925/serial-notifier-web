from aiohttp import web


@web.middleware
async def db_session_middleware_mock(request, handler):
    request['db_session'] = request.app['db_session']
    return await handler(request)
