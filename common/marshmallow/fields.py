import typing

from marshmallow import fields


class EnumField(fields.String):

    def __init__(self, enum_class, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enum_class = enum_class

    def _serialize(self, value, attr, obj, **kwargs) -> typing.Optional[str]:
        if value is None:
            return None
        if isinstance(value, (str, bytes)):
            return super()._serialize(value, attr, obj, **kwargs)
        return value.value

    def _deserialize(self, value, attr, data, **kwargs) -> typing.Any:
        deserialized_value = super()._deserialize(value, attr, data, **kwargs)
        try:
            return self.enum_class[deserialized_value]
        except KeyError:
            return deserialized_value
