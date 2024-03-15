from django_napse.core.models.bots.controller import Controller
from django_napse.core.tasks.base_task import BaseTask


class OrderProcessExecutorTask(BaseTask):
    """Task to process all pending orders."""

    name = "order_process_executor"
    interval_time = 5  # Impossible to make dynamic modification because of celery
    wait_for = "candle_collector"
    color = "\x1b[33;20m"

    def _run(self) -> None:
        """Run a task to process all pending orders."""
        processed_orders = []
        for controller in Controller.objects.all():
            orders, batches = controller.process_orders__no_db(testing=True)
            processed_orders = [*processed_orders, *orders]
            controller.apply_batches(batches)
            controller.apply_orders(orders)
            for order in orders:
                order.apply_modifications()
                order.process_payout()

        if len(processed_orders) > 0:
            self.info(f"Processed {len(processed_orders)} orders. IDs = " + f"{[str(order.pk) for order in processed_orders]}")


OrderProcessExecutorTask().delete_task()
OrderProcessExecutorTask().register_task()
