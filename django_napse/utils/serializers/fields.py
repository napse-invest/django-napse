import uuid
from datetime import datetime


def instance_check(target_type) -> callable:
    def _instance_check(instance, target_type=target_type):
        return isinstance(instance, target_type)

    return _instance_check


class Field:
    validate = None
    # Define if the getter method takes the serializer as argument.
    getter_takes_serializer = False

    def __init__(self, required: bool = False, source: str | None = None):
        self.required = required
        self.source = source

    def to_value(self, value):
        """Overwrite this method for custom transformation on the serialized value."""
        return value

    def as_getter(self, serializer_field_name, serializer_cls) -> None:
        """Return a getter method for the field."""
        return


class StrField(Field):
    to_value: callable = staticmethod(str)
    validate: callable = staticmethod(instance_check(str))


class IntField(Field):
    to_value: callable = staticmethod(int)
    validate: callable = staticmethod(instance_check(int))


class FloatField(Field):
    to_value: callable = staticmethod(float)
    validate: callable = staticmethod(instance_check(float))


class BoolField(Field):
    to_value: callable = staticmethod(bool)
    validate: callable = staticmethod(instance_check(bool))


class UUIDField(Field):
    to_value: callable = staticmethod(uuid.UUID)
    validate: callable = staticmethod(instance_check(uuid.UUID))

    @staticmethod
    def to_value(value):
        if not isinstance(value, uuid.UUID):
            return str(uuid.UUID(value))
        return str(value)


class DatetimeField(Field):
    # to_value: callable = staticmethod(datetime)
    validate: callable = instance_check(datetime)

    @staticmethod
    def to_value(value):
        return value.strftime("%Y-%m-%d %H:%M:%S")


class MethodField(Field):
    getter_takes_serializer = True

    # Avoir type serialization on data
    to_value = None
    validate = None

    def __init__(self, method_name: str | None = None, **kwargs):
        super().__init__(**kwargs)
        self.method_name = method_name

    def as_getter(self, serializer_field_name, serializer_cls) -> callable:
        """Get the (get_<field> | method_name) method from the serializer class."""
        return getattr(
            serializer_cls,
            self.method_name or f"get_{serializer_field_name}",
        )
