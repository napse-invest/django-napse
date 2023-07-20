import celery
from celery.utils.log import get_task_logger
from django.db import IntegrityError
from django.db.utils import ProgrammingError
from django_celery_beat.models import IntervalSchedule, PeriodicTask

from django_napse.core.celery_app import celery_app, strategy_log_free


class BaseTask(celery.Task):
    name = "base_task"
    Strategy = strategy_log_free
    logger = get_task_logger(name)
    interval_time = 5  # Impossible to make dynamic modification because of celery

    def run(self):
        pass

    def create_task(self) -> None:
        """Build task feed_bots_with_candles.

        Raises
        ------
        ValidationError: if task already exist
        """
        try:
            schedule = IntervalSchedule.objects.get(every=self.interval_time, period=IntervalSchedule.SECONDS)
        except ProgrammingError:
            return
        except IntervalSchedule.DoesNotExist:
            schedule = IntervalSchedule.objects.create(every=self.interval_time, period=IntervalSchedule.SECONDS)
        try:
            PeriodicTask.objects.create(interval=schedule, name=f"period_{self.name}", task=self.name)
            self.logger.info(f"Period task {self.name} created")
        except IntegrityError:
            pass

    def delete_task(self) -> None:
        """Destroy task feed_bots_with_candles.

        Raises
        ------
        ValidationError: if task doesn't exist
        """
        try:
            PeriodicTask.objects.get(task=self.name).delete()
            self.logger.info(f"Period task {self.name} deleted")
        except PeriodicTask.DoesNotExist:
            pass
        except ProgrammingError:
            pass

    def register_task(self):
        celery_app.register_task(self)
        self.create_task()
        self.logger.info(f"Period task {self.name} registered")

    def active_tasks(self):
        return celery_app.control.inspect().active()

    def num_active_tasks(self):
        active_tasks = self.active_tasks()
        count = 0
        for worker in active_tasks:
            for task in active_tasks[worker]:
                if task["name"] == self.name:
                    count += 1
        return count

    def avoid_overlap(self, verbose=False):
        if self.num_active_tasks() > 1:
            if verbose:
                self.logger.info(f"Period task {self.name} already running")
            return False
        return True
