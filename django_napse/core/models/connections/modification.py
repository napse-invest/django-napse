from django.db import models

from django_napse.utils.usefull_functions import process_value_from_type


class Modification(models.Model):
    order = models.ForeignKey("Order", on_delete=models.CASCADE, related_name="modifications")

    applied = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    ignore_failed_order = models.BooleanField(default=False)

    key = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    target_type = models.CharField(max_length=100)

    def __str__(self) -> str:  # pragma: no cover
        return f"Modification: id{self.id}; order: {self.order}"


class SpecificArgsModification(Modification):
    connection_specific_arg = models.ForeignKey("ConnectionSpecificArgs", on_delete=models.CASCADE, related_name="modifications")

    def apply(self):
        self._apply(None)
        self.connection_specific_arg.save()
        self.save()

    def _apply(self, bot):
        self.connection_specific_arg.value = self.value
        self.applied = True


class BotModification(Modification):
    def apply(self):
        bot = self.order.bot.find()
        self._apply(bot)
        bot.save()
        self.save()

    def _apply(self, bot):
        if not hasattr(bot, self.key):
            error_msg: str = f"Bot {bot} must have attribute {self.key}"
            raise ValueError(error_msg)
        value = process_value_from_type(self)
        setattr(bot, self.key, value)
        self.applied = True
