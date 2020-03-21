from functools import wraps

from aiohttp import web
from marshmallow import ValidationError

from common.rest_api.error import gen_error_payload, error_response_schema


def validate_payload(schema):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, request, *args, **kwargs):
            try:
                payload = schema.loads(await request.text())
            except ValidationError as err:
                return web.HTTPBadRequest(
                    text=error_response_schema.dumps(gen_error_payload(err))
                )
            return await func(self, request, *args, payload=payload, **kwargs)
        return wrapper
    return decorator
