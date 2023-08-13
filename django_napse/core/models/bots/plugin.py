from django.db import models

from django_napse.core.models.bots.managers.plugin import PluginManager
from django_napse.utils.findable_class import FindableClass


class Plugin(models.Model, FindableClass):
    strategy = models.ForeignKey("Strategy", on_delete=models.CASCADE, related_name="plugins")
    category = models.CharField(max_length=255)

    objects = PluginManager()

    def __str__(self):
        return f"PLUGIN {self.pk=}"

    def info(self, verbose=True, beacon=""):
        string = ""
        string += f"{beacon}Plugin {self.pk}:\n"
        string += f"{beacon}Args:\n"
        string += f"{beacon}\t{self.category=}\n"
        return string

    @classmethod
    def plugin_category(cls):
        if cls == Plugin:
            error_msg = "plugin_category not implemented for the Plugin base class, please implement it in a subclass."
        else:
            error_msg = f"plugin_category not implemented for the Plugin base class, please implement it in the {cls} class."
        raise NotImplementedError(error_msg)

    def _connect(self, connection):
        if self.__class__ == Plugin:
            error_msg = "connect not implemented for the Plugin base class, please implement it in a subclass."
        else:
            error_msg = f"connect not implemented for the Plugin base class, please implement it in the {self.__class__} class."
        raise NotImplementedError(error_msg)

    def connect(self, connection):
        self = self.find()
        return self._connect(connection)

    def _apply(self, data: dict) -> dict:
        if self.__class__ == Plugin:
            error_msg = "_apply not implemented for the Plugin base class, please implement it in a subclass."
        else:
            error_msg = f"_apply not implemented for the Plugin base class, please implement it in the {self.__class__} class."
        raise NotImplementedError(error_msg)

    def apply(self, data: dict) -> dict:
        self = self.find()
        return self._apply(data)
