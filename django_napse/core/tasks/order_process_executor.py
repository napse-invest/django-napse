# from django_napse.core.models import Order
from django_napse.core.tasks.base_task import BaseTask


class OrderProcessExecutorTask(BaseTask):
    name = "order_process_executor"
    interval_time = 5  # Impossible to make dynamic modification because of celery

    def run(self) -> None:
        """Run a task to process all pending orders."""
        if not self.avoid_overlap(verbose=False):
            return
        self.info("Running ControllerUpdateTask")
        # for order in Order.objects.filter(status="pending", completed=True):
        #     order = processor.process_order(order)


OrderProcessExecutorTask().delete_task()
OrderProcessExecutorTask().register_task()
