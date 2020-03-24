from enum import Enum

import pytest
from marshmallow import Schema

from common.marshmallow.fields import EnumField


class TestEnum(Enum):
    TEST_VALUE = 'TEST_VALUE'


class TestSchema(Schema):
    code = EnumField(TestEnum, required=True)


@pytest.mark.parametrize(
    'expected, data', (
            ('{"code": "TEST_VALUE"}', {'code': TestEnum.TEST_VALUE}),
            ('{"code": "SOME_STR"}', {'code': 'SOME_STR'}),
    )
)
def test_enum_field__serialize_enum_field__success(expected, data):
    schema = TestSchema()
    res = schema.dumps(data)

    assert expected == res


@pytest.mark.parametrize(
    'expected, data', (
            ({'code': TestEnum.TEST_VALUE}, '{"code": "TEST_VALUE"}'),
            ({'code': 'SOME_STR'}, '{"code": "SOME_STR"}'),
    )
)
def test_enum_field__deserialize__success(expected, data):
    schema = TestSchema()
    res = schema.loads(data)

    assert expected == res
