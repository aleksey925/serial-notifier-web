import typing

from marshmallow import fields


class EnumField(fields.String):

    def __init__(self, enum_class, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enum_class = enum_class

    def _serialize(self, value, attr, obj, **kwargs) -> typing.Optional[str]:
        if value is None:
            return None
        return value.value

    def _deserialize(self, value, attr, data, **kwargs) -> typing.Any:
        deserialized_value = super()._deserialize(value, attr, data, **kwargs)
        return self.enum_class[deserialized_value]
