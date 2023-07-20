from django_napse.core.models import Controller
from django_napse.core.tasks.base_tasks import BaseTask


class ControllerUpdateTask(BaseTask):
    name = "controller_update"
    interval_time = 45
    time_limit = 60
    soft_time_limit = 60

    def run(self):
        """Run a task to update all controllers."""
        print("ControllerUpdateTask")
        if not self.avoid_overlap(verbose=True):
            print("skipped")
            return
        for controller in Controller.objects.all():
            controller._update_variables()
            controller._get_price()


ControllerUpdateTask().delete_task()
ControllerUpdateTask().register_task()

print("ControllerUpdateTask registered")
