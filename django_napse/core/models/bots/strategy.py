from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import models

from django_napse.core.models.bots.managers.strategy import StrategyManager
from django_napse.utils.findable_class import FindableClass

if TYPE_CHECKING:
    from django_napse.core.models.bots.architecture import Architecture
    from django_napse.core.models.bots.config import BotConfig
    from django_napse.core.models.connections.connection import Connection


class Strategy(models.Model, FindableClass):
    """Define the bot's buying and selling logic."""

    config: BotConfig = models.ForeignKey("BotConfig", on_delete=models.CASCADE, related_name="strategy")
    architecture: Architecture = models.OneToOneField("Architecture", on_delete=models.CASCADE, related_name="strategy")

    objects: StrategyManager = StrategyManager()

    def __str__(self) -> str:  # pragma: no cover
        return f"STRATEGY {self.pk}"

    def info(self, beacon: str = "", *, verbose: bool = True) -> str:
        """Return a string with the model information.

        Args:
            beacon (str, optional): The prefix for each line. Defaults to "".
            verbose (bool, optional): Whether to print the string. Defaults to True.

        Returns:
            str: The string with the history information.
        """
        string = ""
        string += f"{beacon}Strategy {self.pk}:\n"
        string += f"{beacon}Args:\n"
        string += f"{beacon}\t{self.config=}\n"
        string += f"{beacon}\t{self.architecture=}\n"

        if verbose:
            print(string)
        return string

    def give_order(self, data: dict) -> list[dict]:
        if self.__class__ == Strategy:
            error_msg = "give_order not implemented for the Strategy base class, please implement it in a subclass."
        else:
            error_msg = f"give_order not implemented for the Strategy base class, please implement it in the {self.__class__} class."
        raise NotImplementedError(error_msg)

    @classmethod
    def plugin_classes(cls) -> list:
        """Return the list of all strategy's plugins."""
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
    def architecture_class(cls) -> Architecture:
        """Return the class of the associated architecture."""
        return cls._meta.get_field("architecture").related_model

    @property
    def variables(self) -> dict[str, any]:
        """Return variables of a strategy."""
        self = self.find(self.pk)
        variables = {}
        for variable in self._meta.get_fields():
            if variable.name.startswith("variable_"):
                variables[variable.name[8:]] = getattr(self, variable.name)
        return variables

    def connect(self, connection: Connection) -> None:
        return

    def copy(self) -> Strategy:
        """Return a copy of the Strategy."""
        return self.find().__class__.objects.create(
            config=self.config.find().duplicate_immutable(),
            architecture=self.architecture.find().copy(),
        )
