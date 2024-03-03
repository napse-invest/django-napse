import uuid
from datetime import datetime
from typing import Optional


def instance_check(target_type: any) -> callable:
    """Produce a callable to check if an instance is of a specific type."""

    def _instance_check(instance: object, target_type: any = target_type) -> bool:
        return isinstance(instance, target_type)

    return _instance_check


class Field:
    """Fields represent models' fields in the serializer."""

    validate = None
    # Define if the getter method takes the serializer as argument.
    getter_takes_serializer = False

    def __init__(
        self,
        *,
        default: Optional[any] = None,
        source: str | None = None,
        required: bool = False,
        **kwargs: dict[str, any],  # noqa: ARG002 (for DRF compatibility)
    ) -> None:
        """Define basic parameters of the field.

        Parameters:
            required: bool
                Define if the field is required. Only used for validation.
            source: str
                Define the source of the field in the model (ex: `exchange.name`).
        """
        self.required = required
        self.source = source
        self.default = default

    def to_value(self, value: any) -> any:
        """Overwrite this method for custom transformation on the serialized value."""
        return value

    def as_getter(self, serializer_field_name: str, serializer_cls: type) -> None:  # noqa: ARG002
        """Return a getter method for the field."""
        return


class StrField(Field):
    """Represent a string.

    Can be used for model.CharField, model.TextField, ...
    """

    to_value: callable = staticmethod(str)
    validate: callable = staticmethod(instance_check(str))


class IntField(Field):
    """Represent a integer."""

    to_value: callable = staticmethod(int)
    validate: callable = staticmethod(instance_check(int))


class FloatField(Field):
    """Represent a float."""

    to_value: callable = staticmethod(float)
    validate: callable = staticmethod(instance_check(float))


class BoolField(Field):
    """Represent a boolean."""

    to_value: callable = staticmethod(bool)
    validate: callable = staticmethod(instance_check(bool))


class UUIDField(Field):
    """Represent a uuid."""

    to_value: callable = staticmethod(uuid.UUID)
    validate: callable = staticmethod(instance_check(uuid.UUID))

    @staticmethod
    def to_value(value: uuid.UUID | str) -> str:
        """Format & return the value."""
        if not isinstance(value, uuid.UUID):
            return str(uuid.UUID(value))
        return str(value)


class DatetimeField(Field):
    """Represent a date."""

    validate: callable = instance_check(datetime)

    @staticmethod
    def to_value(value: datetime) -> str:
        """Format & return the value."""
        return value.strftime("%Y-%m-%d %H:%M:%S")


class MethodField(Field):
    """MethodField can be used to serialize complexe behaviours."""

    getter_takes_serializer = True

    # Avoir type serialization on data
    to_value = None
    validate = None

    def __init__(self, method_name: str | None = None, **kwargs: dict[str, any]) -> None:
        """Define the method field."""
        super().__init__(**kwargs)
        self.method_name = method_name

    def as_getter(self, serializer_field_name: str, serializer_cls: type) -> callable:
        """Get the (get_<field> | method_name) method from the serializer class."""
        return getattr(
            serializer_cls,
            self.method_name or f"get_{serializer_field_name}",
        )
