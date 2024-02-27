from __future__ import annotations
from django_napse.utils.serializers.fields import Field
import operator
from rest_framework.serializers import ValidationError


class BaseSerializer:
    _fields = {}
    _compiled_fields = {}
    _validators: dict[str, tuple[bool, callable]] = {}


class MetaSerializer(type):
    @staticmethod
    def _compile_fields(fields, serializer_cls: Serializer) -> list[tuple]:
        """Compile a field to give an easy access to all elements of each fields."""

        def _compile_field(field, name, serializer_cls: Serializer) -> tuple:
            """Compile field's elements to tuple."""
            if field.source is not None and "." in field.source:
                getter = (operator.attrgetter(attr) for attr in field.source.split("."))
                getter_is_generator = True
            else:
                getter = field.as_getter(name, serializer_cls) or operator.attrgetter(name)
                getter_is_generator = False
            return (
                name,
                field.to_value,
                field.required,
                getter,
                field.getter_takes_serializer,
                getter_is_generator,
            )

        return [_compile_field(field, name, serializer_cls) for name, field in fields.items()]

    def __new__(
        cls: MetaSerializer,
        name: str,
        bases: tuple,
        attrs: dict,
    ):
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
                fields.update(obj._fields)

        serializer_cls._fields = fields
        serializer_cls._compiled_fields = cls._compile_fields(fields, serializer_cls)
        serializer_cls._validators = {
            name: (
                field.required,
                field.validate,
            )
            for name, field in fields.items()
            if field.validate
        }

        return serializer_cls


class Serializer(BaseSerializer, Field, metaclass=MetaSerializer):
    Model = None

    def __init__(
        self,
        instance=None,
        data=None,
        many=False,
        **kwargs,
    ):
        self._instance = instance
        self._data = data
        self._many = many
        self._validated_data: dict[str, any] | None = None

        if self._data is not None:
            self.validate_data(self._data)

        # To use serializer in serializer
        super().__init__(**kwargs)

    @property
    def data(self):
        if self._data is not None:
            return self._data
        return self.to_value()

    @property
    def validated_data(self):
        if self._validated_data is None:
            error_msg: str = "Data are invalid"
            raise ValueError(error_msg)
        return self._validated_data

    def to_value(self, instance: any | None = None) -> any:
        """Serialize instance."""
        instance = instance or self._instance
        if self._many:
            return [self._serialize(ist, self._compiled_fields) for ist in instance]
        return self._serialize(instance, self._compiled_fields)

    def _serialize(self, instance, fields):
        serialized_instance = {}
        for name, to_value, required, getter, getter_takes_serializer, getter_is_generator in fields:
            try:
                if getter_is_generator:
                    value = instance
                    for get in getter:
                        value = get(value)
                else:
                    value = getter(self, instance) if getter_takes_serializer else getter(instance)
            except (AttributeError, KeyError):
                if required:
                    error_msg: str = f"Field {name} is required."
                    raise ValueError(error_msg) from None
                continue
            if to_value:
                value = to_value(value)
            serialized_instance[name] = value
        return serialized_instance

    def validate_data(self, data):
        if not isinstance(data, dict):
            error_msg: str = "Data must be a dictionary."
            raise ValidationError(error_msg)
        for name, (required, validator) in self._validators.items():
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

        # Retrieve db instances if needed
        for name, field in self._fields.items():
            if isinstance(field, Serializer):
                data[name] = field.get(data[name])

        self._validated_data = data
        return data

    def validate(self, data):
        """Used for automatic validation with serializer.

        Please to not use this method.
        Note: provided data must be id or uuid
        """
        instance = self.get(data)
        data = self.to_value(instance)
        return self.validate_data(data)

    def _model_checks(self, validated_data):
        if not self.Model:
            error_msg: str = "Model is not defined."
            raise ValueError(error_msg)

        if not validated_data:
            error_msg: str = "Data are not validated."
            raise ValueError(error_msg)

    def get(self, data):
        """Retrieve instance from data."""
        try:
            instance = self.Model.objects.get(uuid=data) if hasattr(self.Model, "uuid") else self.Model.objects.get(id=data)
        except (self.Model.DoesNotExist, TypeError):
            error_msg: str = f"Instance with id {data} does not exist."
            raise ValidationError(error_msg) from None
        return instance

    def create(self, validated_data=None):
        validated_data = validated_data or self._validated_data
        self._model_checks(validated_data=validated_data)
        return self.Model.objects.create(**validated_data)

    def update(self, instance, validated_data=None):
        validated_data = validated_data or self._validated_data
        self._model_checks(validated_data=validated_data)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance
