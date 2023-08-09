from django.db import models

from django_napse.utils.errors import ControllerError


class ControllerManager(models.Manager):
    def create(self, **kwargs):
        bypass = kwargs.pop("bypass", False)
        if not bypass:
            error_msg = "Controller.object.create() is not recommended. Use Controller.get() instead."
            raise ControllerError.BypassError(error_msg)
        return super().create(**kwargs)
