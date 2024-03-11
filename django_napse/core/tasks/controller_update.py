from django_napse.core.models import Controller
from django_napse.core.tasks.base_task import BaseTask


class ControllerUpdateTask(BaseTask):
    """Task to update all controllers."""

    name = "controller_update"
    interval_time = 45
    time_limit = 60
    soft_time_limit = 60

    def run(self) -> None:
        """Run a task to update all controllers."""
        if not self.avoid_overlap(verbose=False):
            return
        self.info("Running ControllerUpdateTask")
        for controller in Controller.objects.all():
            controller.update_variables_always()
            controller.get_price_always()


ControllerUpdateTask().delete_task()
ControllerUpdateTask().register_task()
