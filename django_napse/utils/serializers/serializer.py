from __future__ import annotations

import operator
import uuid
from typing import ClassVar

from rest_framework.serializers import ValidationError

from django_napse.utils.serializers.fields import Field


class BaseSerializer:
    """Base class for Serializer."""

    fields_map: ClassVar[dict[str, Field]] = {}
    compiled_fields: ClassVar[
        tuple[
            str,
            callable,
            bool,
            callable,
            bool,
            bool,
        ]
    ] = {}
    validators_map: ClassVar[dict[str, tuple[bool, callable]]] = {}


class MetaSerializer(type):
    """Define the creation of Serializer classes."""

    @staticmethod
    def _compile_fields(fields: dict[str, Field], serializer_cls: Serializer) -> list[tuple]:
        """Compile a field to give an easy access to all elements of each fields."""

        def _compile_field(field: dict[str, Field], name: str, serializer_cls: Serializer) -> tuple:
            """Compile field's elements to tuple."""
            if field.source is not None and "." in field.source:
                getter: set = [operator.attrgetter(attr) for attr in field.source.split(".")]
                getter_is_generator = True
            else:
                getter = field.as_getter(name, serializer_cls) or operator.attrgetter(name)
                getter_is_generator = False
            return (
                name,
                field.default,
                field.to_value,
                getter,
                field.getter_takes_serializer,
                getter_is_generator,
            )

        return [_compile_field(field, name, serializer_cls) for name, field in fields.items()]

    def __new__(cls: MetaSerializer, name: str, bases: tuple, attrs: dict) -> Serializer:
        """Define how to build Serializer classes.

        Args:
            cls: MetaClass class.
            name: Class name.
            bases: Bases of the class.
            attrs: Method and attributs of the class (like Fields).
        """
        fields = {}

        # Get direct Fields from attributs
        fields = {key: value for key, value in attrs.items() if isinstance(value, Field)}
        for key in fields:
            del attrs[key]

        # Make serializer class
        serializer_cls = super(MetaSerializer, cls).__new__(cls, name, bases, attrs)

        # Retrieve Fields from parent classes
        for obj in serializer_cls.__mro__[::-1]:
            if issubclass(obj, BaseSerializer):
                fields.update(obj.fields_map)

        serializer_cls.fields_map = fields
        serializer_cls.compiled_fields = cls._compile_fields(fields, serializer_cls)
        serializer_cls.validators_map = {
            name: (
                field.required,
                field.validate,
            )
            for name, field in fields.items()
            if field.validate
        }

        return serializer_cls


class Serializer(BaseSerializer, Field, metaclass=MetaSerializer):  # noqa
    Model = None
    # If read_only is True, the serializer will not be able to make interaction with the 'Model' class.
    # But it can still be used to serialize or validate data.
    read_only = False

    def __init__(self, instance=None, data=None, many=False, **kwargs):  # noqa
        self._instance = instance
        self._data = data
        self._many = many
        self._validated_data: dict[str, any] | None = None

        if self._data is not None:
            self.validate_data(self._data)

        # To use serializer in serializer
        super().__init__(**kwargs)

        # Save additionnal kwargs for compatibility
        self._kwargs = kwargs

    @property
    def data(self):  # noqa
        if self._data is not None:
            return self._data
        return self.to_value(instance=self._instance)

    @property
    def validated_data(self):  # noqa
        if self._validated_data is None:
            error_msg: str = "Data are invalid"
            raise ValueError(error_msg)
        return self._validated_data

    def to_value(self, instance: object | list[object] | None = None) -> any:
        """Serialize instance."""
        # TODO: make a try & except TypeError | AttributeError (log + return 400) # noqa
        instance = instance or self._instance

        if instance is None:
            return None

        if self._many:
            try:
                len(instance)
            except TypeError:
                instance = instance.all()
            return [self._serialize(ist, self.compiled_fields) for ist in instance]
        return self._serialize(instance, self.compiled_fields)

    def _serialize(self, instance: object, fields: dict[str, Field]) -> dict[str, any]:
        def _get_value(instance, getter, getter_takes_serializer, getter_is_generator):  # noqa
            if getter_is_generator:
                value = instance
                for get in getter:
                    value = get(value)
            else:
                value = getter(self, instance) if getter_takes_serializer else getter(instance)
            return value

        serialized_instance = {}
        for name, default, to_value, getter, getter_takes_serializer, getter_is_generator in fields:
            # Default wrapper around getter for optimization
            if default is None:
                value = _get_value(
                    instance,
                    getter,
                    getter_takes_serializer,
                    getter_is_generator,
                )
            else:
                try:
                    value = _get_value(
                        instance,
                        getter,
                        getter_takes_serializer,
                        getter_is_generator,
                    )
                except AttributeError:
                    value = default

            if to_value:
                value = to_value(value)
            serialized_instance[name] = value
        return serialized_instance

    def validate_data(self, data: dict) -> any:
        """Used for validation with serializer.

        Please to not use this method.
        """
        if not isinstance(data, dict):
            error_msg: str = "Data must be a dictionary."
            raise ValidationError(error_msg)
        validated_data = {}
        for name, (required, validator) in self.validators_map.items():
            elt = data.get(name)
            if elt is None:
                if required:
                    error_msg: str = f"Field {name} is required."
                    raise ValidationError(error_msg)
                continue

            result = validator(elt)
            if not result:
                error_msg: str = f"Field {name} is invalid."
                raise ValidationError(error_msg)
            if isinstance(result, bool):
                validated_data[name] = elt
            else:
                validated_data[name] = result

        self._validated_data = validated_data
        return validated_data

    def validate(self, data: dict | str | int | uuid.UUID) -> any:
        """Used for automatic validation with serializer.

        Please to not use this method.
        """
        if self.read_only:
            error_msg: str = "This serializer is read only."
            raise ValueError(error_msg)

        if isinstance(data, (str, int, uuid.UUID)):
            return self.get(uuid_or_id=data)

        return self.validate_data(data)

    def _model_checks(self, validated_data):  # noqa
        if self.read_only:
            error_msg: str = "This serializer is read only."
            raise ValueError(error_msg)

        if not self.Model:
            error_msg: str = "Model is not defined."
            raise ValueError(error_msg)

        if not validated_data:
            error_msg: str = "Data are not validated."
            raise ValueError(error_msg)

    def get(self, uuid_or_id=None):  # noqa
        """Retrieve instance from data."""
        try:
            instance = self.Model.objects.get(uuid=uuid_or_id) if hasattr(self.Model, "uuid") else self.Model.objects.get(id=uuid_or_id)
        except (self.Model.DoesNotExist, TypeError):
            error_msg: str = f"Instance with id {uuid_or_id} does not exist."
            raise ValidationError(error_msg) from None
        return instance

    def create(self, validated_data=None):  # noqa
        validated_data = validated_data or self._validated_data
        self._model_checks(validated_data=validated_data)
        return self.Model.objects.create(**validated_data)

    def update(self, instance, validated_data=None):  # noqa
        validated_data = validated_data or self._validated_data
        self._model_checks(validated_data=validated_data)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance
