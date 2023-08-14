from django.db import models


class StrategyManager(models.Manager):
    def create(self, **kwargs):
        architecture = kwargs["architecture"]
        config = kwargs["config"]
        if architecture.__class__ != self.model.architecture_class():
            error_msg = f"architecture must be of type {self.model.architecture_class().__name__}"
            raise TypeError(error_msg)
        if config.__class__ != self.model.config_class():
            error_msg = f"config must be of type {self.model.config_class().__name__}"
            raise TypeError(error_msg)
        strategy = self.model(**kwargs)
        strategy.save()
        for plugin in self.model.plugin_classes():
            plugin.objects.create(strategy=strategy)
        return strategy
