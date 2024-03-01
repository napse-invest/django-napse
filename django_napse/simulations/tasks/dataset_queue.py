from django_napse.core.tasks import BaseTask
from django_napse.simulations.models import DataSetQueue
from django_napse.utils.errors import SimulationError


class DataSetQueueTask(BaseTask):
    """Task to process DataSetQueues."""

    name = "dataset_queue"
    interval_time = 5
    time_limit = 60 * 60
    soft_time_limit = 60 * 60

    def run(self) -> None:
        """Run a task to process all DataSetQueues.

        Raises:
            SimulationError.DataSetQueueError: If the DataSetQueue is not finished.
        """
        if not self.avoid_overlap(verbose=False):
            return
        self.info("Running DataSetQueueTask")
        queue = DataSetQueue.objects.all().order_by("created_at").first()
        if queue is None:
            return
        try:
            queue.download()
        except TimeoutError:
            return
        if queue.is_finished():
            queue.delete()
        else:
            dataset = queue.get_dataset()
            error_msg = f"DataSetQueueTask: {queue} status {dataset.status} completion {dataset.completion}"
            raise SimulationError.DataSetQueueError(error_msg)


DataSetQueueTask().delete_task()
DataSetQueueTask().register_task()
