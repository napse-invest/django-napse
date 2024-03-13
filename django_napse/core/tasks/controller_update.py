from django_napse.core.models import Controller
from django_napse.core.tasks.base_task import BaseTask


class ControllerUpdateTask(BaseTask):
    """Task to update all controllers."""

    name = "controller_update"
    interval_time = 15
    time_limit = 60
    soft_time_limit = 60

    def _run(self) -> None:
        """Run a task to update all controllers."""
        self.info("Running ControllerUpdateTask")
        for controller in Controller.objects.all():
            controller.update_variables_always()
            controller.get_price_always()


ControllerUpdateTask().delete_task()
ControllerUpdateTask().register_task()
