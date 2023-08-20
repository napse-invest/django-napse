# from django_napse.core.models import Order
from django_napse.core.tasks.base_tasks import BaseTask


class OrderProcessExecutorTask(BaseTask):
    name = "order_process_executor"
    interval_time = 5  # Impossible to make dynamic modification because of celery

    def run(self):
        """Run TASK.

        Process orders from bots to make buy/sell on binance.
        """
        print("OrderProcessExecutorTask")
        if not self.avoid_overlap(verbose=True):
            print("skipped")
            return
        # for order in Order.objects.filter(status="pending", completed=True):
        #     order = processor.process_order(order)


OrderProcessExecutorTask().delete_task()
OrderProcessExecutorTask().register_task()
