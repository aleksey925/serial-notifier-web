import logging
from enum import Enum
from functools import wraps

from aiohttp import web
from marshmallow import ValidationError, Schema, fields

from common.marshmallow.fields import EnumField
from common.rest_api.exceptions import NotValidDataError, SnBaseException

logger = logging.getLogger()


class ErrorCodes(Enum):
    VALIDATION_ERROR = 'VALIDATION_ERROR'
    UNEXPECTED_ERROR = 'UNEXPECTED_ERROR'


class ErrorResponseSchema(Schema):
    code = EnumField(ErrorCodes, required=True)
    message = fields.String(required=True)
    error_fields = fields.Dict()


error_response_schema = ErrorResponseSchema()


MAP_ERROR_CODE_ON_HTTP_ERR = {
    ErrorCodes.VALIDATION_ERROR: web.HTTPBadRequest,
    ErrorCodes.UNEXPECTED_ERROR: web.HTTPServerError,
}

MAP_ERROR_CODE_ON_MSGS = {
    ErrorCodes.VALIDATION_ERROR: 'Data is not valid',
    ErrorCodes.UNEXPECTED_ERROR: 'There was an unexpected error',
}

MAP_EXCEPTION_ON_CODE_ERROR = {
    ValidationError: ErrorCodes.VALIDATION_ERROR,
    NotValidDataError: ErrorCodes.VALIDATION_ERROR,
}

ERROR_FIELDS_EXTRACTOR = {
    ValidationError: lambda i: i.messages,
    NotValidDataError: lambda i: i.messages,
}


def error_handler(func):
    """
    Декоратор автоматизирующий генерацию HTTP response на основании возникшего
    исключения
    :param func: декорируемое представление (views)
    :return: обернутое представление (view)
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except SnBaseException as err:
            return gen_http_response(err)
        except Exception as err:
            logger.exception(
                f'Возникла непредвиденная ошибка при выполнеии {func.__name__}'
            )
            return gen_http_response(err)
    return wrapper


def gen_http_response(exception: Exception):
    payload = gen_error_payload(exception)
    resp_class = MAP_ERROR_CODE_ON_HTTP_ERR.get(payload['code'])
    return resp_class(text=error_response_schema.dumps(payload))


def gen_error_payload(exception: Exception) -> dict:
    code = MAP_EXCEPTION_ON_CODE_ERROR.get(
        exception.__class__, ErrorCodes.UNEXPECTED_ERROR
    )
    error_field = ERROR_FIELDS_EXTRACTOR.get(
        exception.__class__, lambda i: tuple()
    )(exception)

    if isinstance(exception, SnBaseException) and not error_field:
        message = str(exception)
    else:
        message = MAP_ERROR_CODE_ON_MSGS.get(code)

    return {
        'code': code,
        'message': message,
        'error_fields': error_field
    }
