from django_napse.utils.constants import MODIFICATION_STATUS
from django_napse.utils.usefull_functions import process_value_from_type

from .modification import Modification


class StrategyModification(Modification):
    def apply(self):
        strategy = self.order.connection.bot.strategy.find()
        strategy, self = self._apply(strategy)
        strategy.save()
        self.save()

    def _apply(self, **kwargs):
        strategy = kwargs.get("strategy")
        if not hasattr(strategy, f"variable_{self.key}"):
            error_msg: str = f"Strategy {strategy} must have attribute variable_{self.key}"
            raise ValueError(error_msg)
        setattr(strategy, f"variable_{self.key}", process_value_from_type(self.value, self.target_type))
        self.status = MODIFICATION_STATUS.APPLIED
        return strategy, self
