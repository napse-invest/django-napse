from django.db import models

from django_napse.utils.constants import MODIFICATION_STATUS
from django_napse.utils.findable_class import FindableClass
from django_napse.utils.usefull_functions import process_value_from_type


class Modification(models.Model, FindableClass):
    """A modification to be applied to an order."""

    order = models.ForeignKey("Order", on_delete=models.CASCADE, related_name="modifications")

    status = models.CharField(default=MODIFICATION_STATUS.PENDING, max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    ignore_failed_order = models.BooleanField(default=False)

    key = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    target_type = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f"MODIFICATION: {self.pk=}"

    def get_value(self, **kwargs: dict[str, any]) -> any:
        """Return value into classic python object."""
        return process_value_from_type(self.value, self.target_type, **kwargs)

    def apply__no_db(self) -> tuple[models.Model, "Modification"]:
        """Apply the modification without saving it to the database.

        Raises:
            NotImplementedError: You must implement this method in your subclass.
        """
        error_msg = "You must implement this method in your subclass"
        raise NotImplementedError(error_msg)

    def apply(self) -> None:
        """Apply the modification to the order and save them to the database.

        Raises:
            NotImplementedError: You must implement this method in your subclass.
        """
        error_msg = "You must implement this method in your subclass"
        raise NotImplementedError(error_msg)
