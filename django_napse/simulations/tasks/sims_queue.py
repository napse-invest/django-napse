from django_napse.core.tasks import BaseTask
from django_napse.simulations.models import BotSimQueue
from django_napse.utils.errors import SimulationError


class BotSimQueueTask(BaseTask):
    name = "sim_queue"
    interval_time = 5
    time_limit = 60 * 60
    soft_time_limit = 60 * 60

    def run(self):
        """Run TASK.

        Process all pending Sims one by one.
        """
        if not self.avoid_overlap(verbose=True):
            return
        queue = BotSimQueue.objects.filter(error=False).order_by("created_at").first()

        if queue is None:
            return
        if queue.status == "RUNNING":
            return
        try:
            queue.run_quicksim()
            queue = BotSimQueue.objects.get(simulation_reference=queue.simulation_reference)
        except SimulationError.CancelledSimulationError:
            print("BotSimQueueTask: cancelled")
            queue.delete()
            return
        except Exception as e:
            print("BotSimQueueTask: error")
            print(str(e))
            queue.error = True
            queue.save()
            raise e

        if queue.is_finished():
            print("BotSimQueueTask: finished")
            queue.delete()
        else:
            error_msg = f"SimQueueTask: {queue} status {queue.status} completion {queue.completion}"
            raise SimulationError.BotSimQueueError(error_msg)


BotSimQueueTask().delete_task()
BotSimQueueTask().register_task()
