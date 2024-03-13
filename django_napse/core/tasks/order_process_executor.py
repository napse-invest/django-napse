from django_napse.core.models.bots.controller import Controller
from django_napse.core.tasks.base_task import BaseTask


class OrderProcessExecutorTask(BaseTask):
    """Task to process all pending orders."""

    name = "order_process_executor"
    interval_time = 5  # Impossible to make dynamic modification because of celery

    def _run(self) -> None:
        """Run a task to process all pending orders."""
        self.info("Running OrderProcessExecutorTask")
        processed = 0
        for controller in Controller.objects.all():
            orders, batches = controller.process_orders__no_db(testing=True)
            processed += len(orders)
            controller.apply_batches(batches)
            controller.apply_orders(orders)
            for order in orders:
                order.apply_modifications()
                order.process_payout()

        if processed > 0:
            self.info(f"Processed {processed} orders")


OrderProcessExecutorTask().delete_task()
OrderProcessExecutorTask().register_task()
