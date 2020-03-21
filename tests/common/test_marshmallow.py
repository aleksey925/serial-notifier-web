from enum import Enum

from marshmallow import Schema

from common.marshmallow.fields import EnumField


class TestEnum(Enum):
    TEST_VALUE = 'TEST_VALUE'


class TestSchema(Schema):
    code = EnumField(TestEnum, required=True)


def test_enum_field__serialize():
    data = {'code': TestEnum.TEST_VALUE}
    expected = '{"code": "TEST_VALUE"}'

    schema = TestSchema()
    res = schema.dumps(data)

    assert expected == res


def test_enum_field__deserialize():
    data = '{"code": "TEST_VALUE"}'
    expected = {'code': TestEnum.TEST_VALUE}

    schema = TestSchema()
    res = schema.loads(data)

    assert expected == res
