from django.db import models

from django_napse.core.models.bots.managers.plugin import PluginManager
from django_napse.utils.findable_class import FindableClass


class Plugin(models.Model, FindableClass):
    """A plugin is a pluggable extention to a bot."""

    strategy = models.ForeignKey("Strategy", on_delete=models.CASCADE, related_name="plugins")
    category = models.CharField(max_length=255)

    objects = PluginManager()

    def __str__(self) -> str:
        return f"PLUGIN {self.pk=}"

    def info(self, beacon: str = "", *, verbose: bool = True) -> str:
        """Return a string with the model information.

        Args:
            beacon (str, optional): The prefix for each line. Defaults to "".
            verbose (bool, optional): Whether to print the string. Defaults to True.

        Returns:
            str: The string with the history information.
        """
        string = ""
        string += f"{beacon}Plugin {self.pk}:\n"
        string += f"{beacon}Args:\n"
        string += f"{beacon}\t{self.category=}\n"

        if verbose:
            print(string)
        return string

    @classmethod
    def plugin_category(cls):  # noqa
        if cls == Plugin:
            error_msg = "plugin_category not implemented for the Plugin base class, please implement it in a subclass."
        else:
            error_msg = f"plugin_category not implemented for the Plugin base class, please implement it in the {cls} class."
        raise NotImplementedError(error_msg)

    def _connect(self, connection):  # noqa
        if self.__class__ == Plugin:
            error_msg = "connect not implemented for the Plugin base class, please implement it in a subclass."
        else:
            error_msg = f"connect not implemented for the Plugin base class, please implement it in the {self.__class__} class."
        raise NotImplementedError(error_msg)

    def connect(self, connection):  # noqa
        self = self.find()
        return self._connect(connection)

    def apply__no_db(self, data: dict) -> dict:
        if self.__class__ == Plugin:
            error_msg = "apply__no_db not implemented for the Plugin base class, please implement it in a subclass."
        else:
            error_msg = f"apply__no_db not implemented for the Plugin base class, please implement it in the {self.__class__} class."
        raise NotImplementedError(error_msg)

    def apply(self, data: dict) -> dict:
        self = self.find()
        return self.apply__no_db(data)
