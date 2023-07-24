from django.db import models

from django_napse.utils.findable_class import FindableClass


class Strategy(models.Model, FindableClass):
    plugins = []

    def __str__(self) -> str:
        return f"STRATEGY {self.pk}"

    def give_order(self, data: dict):
        error_msg = "give_order not implemented for the Strategy base class, please implement it in the child class."
        raise NotImplementedError(error_msg)
