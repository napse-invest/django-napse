from django.db import models

from django_napse.utils.constants import PLUGIN_CATEGORIES
from django_napse.utils.errors import PluginError


class PluginManager(models.Manager):
    def create(self, strategy):
        if self.plugin_category not in PLUGIN_CATEGORIES:
            error_msg = f"Invalid plugin category: {self.plugin_category}"
            raise PluginError.InvalidPluginCategory(error_msg)
        plugin = self.model(strategy=strategy, category=self.plugin_category)
        plugin.save()
        return plugin
