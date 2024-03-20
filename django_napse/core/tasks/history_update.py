from django_napse.core.models.histories.history import History
from django_napse.core.tasks.base_task import BaseTask


class HistoryUpdateTask(BaseTask):
    """Task to update all histories."""

    name = "history_update"
    interval_time = 3600
    time_limit = 60
    soft_time_limit = 60

    def _run(self) -> None:
        """Run a task to update all controllers."""
        for history in History.objects.all():
            history.find().generate_data_point()


HistoryUpdateTask().delete_task()
HistoryUpdateTask().register_task()
