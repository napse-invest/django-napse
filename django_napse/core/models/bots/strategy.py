from django.db import models

from django_napse.core.models.bots.managers.strategy import StrategyManager
from django_napse.utils.findable_class import FindableClass


class Strategy(models.Model, FindableClass):
    config = models.OneToOneField("BotConfig", on_delete=models.CASCADE, related_name="strategy")
    architecture = models.OneToOneField("Architecture", on_delete=models.CASCADE, related_name="strategy")

    objects = StrategyManager()

    def __str__(self) -> str:  # pragma: no cover
        return f"STRATEGY {self.pk}"

    def give_order(self, data: dict) -> list[dict]:
        if self.__class__ == Strategy:
            error_msg = "give_order not implemented for the Strategy base class, please implement it in a subclass."
        else:
            error_msg = f"give_order not implemented for the Strategy base class, please implement it in the {self.__class__} class."
        raise NotImplementedError(error_msg)

    @classmethod
    def plugin_classes(cls):
        return []

    @classmethod
    def achitecture_class(cls):
        if cls == Strategy:
            error_msg = "achitecture_class not implemented for the Strategy base class, please implement it in a subclass."
        else:
            error_msg = f"achitecture_class not implemented for the Strategy base class, please implement it in the {cls} class."
        raise NotImplementedError(error_msg)

    @classmethod
    def config_class(cls):
        if cls == Strategy:
            error_msg = "config_class not implemented for the Strategy base class, please implement it in a subclass."
        else:
            error_msg = f"config_class not implemented for the Strategy base class, please implement it in the {cls} class."
        raise NotImplementedError(error_msg)

    @classmethod
    def architecture_class(cls):
        return cls._meta.get_field("architecture").related_model

    @property
    def variables(self):
        self = self.find(self.pk)
        variables = {}
        for variable in self._meta.get_fields():
            if variable.name.startswith("variable_"):
                variables[variable.name[8:]] = getattr(self, variable.name)
        return variables

    def connect(self, connection):
        return

    def copy(self):
        return self.find().__class__.objects.create(
            config=self.config.find().duplicate_immutable(),
            architecture=self.architecture.find().copy(),
        )
