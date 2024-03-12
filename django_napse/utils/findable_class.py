from typing import TypeVar

from django.apps import apps

T = TypeVar("T", bound="FindableClass")


class FindableClass:
    """Class to find the correct subclass of a django model."""

    def find(self: T) -> T:
        """Find the correct subclass of this django model."""
        instance = self

        for subclass in self.__class__.__subclasses__():
            django_model = apps.get_model(self._meta.app_label, f"{subclass.__name__}")
            try:
                instance = django_model.objects.get(pk=instance.pk)
                break
            except django_model.DoesNotExist:
                pass
        return instance
