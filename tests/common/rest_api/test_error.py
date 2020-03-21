import json

import pytest
from aiohttp import web
from marshmallow import ValidationError

from common.rest_api.error import (
    gen_error_payload, ErrorCodes, gen_http_response
)
from common.rest_api.exceptions import NotValidDataError, SnBaseException


class SomeException(Exception):
    pass


class SomeProjectException(SnBaseException):
    pass


expected_payloads = {
    Exception(): {
        'code': ErrorCodes.UNEXPECTED_ERROR,
        'message': 'There was an unexpected error',
        'error_fields': ()
    },
    SomeException('some text'): {
        'code': ErrorCodes.UNEXPECTED_ERROR,
        'message': 'There was an unexpected error',
        'error_fields': ()
    },
    SomeProjectException('some text'): {
        'code': ErrorCodes.UNEXPECTED_ERROR,
        'message': 'some text',
        'error_fields': ()
    },
    ValidationError({'email': ['email not valid']}): {
        'code': ErrorCodes.VALIDATION_ERROR,
        'message': 'Data is not valid',
        'error_fields': {'email': ['email not valid']}
    },
    NotValidDataError('email not valid', 'email'): {
        'code': ErrorCodes.VALIDATION_ERROR,
        'message': 'Data is not valid',
        'error_fields': {'email': ['email not valid']}
    },
}

_http_exc = [
    web.HTTPServerError, web.HTTPServerError, web.HTTPServerError,
    web.HTTPBadRequest, web.HTTPBadRequest
]
expected_http_exceptions = [
    (i[0], i[1], exc)
    for i, exc in zip(tuple(expected_payloads.items()), _http_exc)
]


@pytest.mark.parametrize('exc, expected_payload', (expected_payloads.items()))
def test_gen_error_payload(exc, expected_payload):
    payload = gen_error_payload(exc)

    assert expected_payload == payload


@pytest.mark.parametrize(
    'exc, expected_payload, http_exc', expected_http_exceptions
)
def test_gen_http_response(exc, expected_payload, http_exc):
    return_exc = gen_http_response(exc)
    return_payload = json.loads(return_exc.text)

    assert return_exc.__class__ == http_exc
    assert return_payload['code'] == expected_payload['code'].value
    assert return_payload['message'] == expected_payload['message']
    if isinstance(return_payload['error_fields'], list):
        assert tuple(return_payload['error_fields']) == (
            expected_payload['error_fields']
        )
    else:
        assert return_payload['error_fields'] == (
            expected_payload['error_fields']
        )
