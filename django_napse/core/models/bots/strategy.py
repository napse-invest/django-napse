from django.db import models

from django_napse.utils.findable_class import FindableClass


class Strategy(models.Model, FindableClass):
    plugins = []

    def __str__(self) -> str:  # pragma: no cover
        return f"STRATEGY {self.pk}"

    def give_order(self, data: dict) -> list[dict]:
        error_msg = f"give_order not implemented for the Strategy base class, please implement it in the {self.__class__} class."
        raise NotImplementedError(error_msg)

    @classmethod
    def config_class(cls):
        return cls._meta.get_field("config").related_model

    @classmethod
    def architecture_class(cls):
        return cls._meta.get_field("architecture").related_model

    def copy(self):
        return self.find().__class__.objects.create(
            config=self.config.duplicate_immutable(),
            architecture=self.architecture.copy(),
        )
