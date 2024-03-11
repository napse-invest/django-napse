from datetime import datetime, timezone
from typing import Optional

import celery
from celery.utils.log import get_task_logger
from django.db import IntegrityError
from django.db.utils import ProgrammingError
from django_celery_beat.models import IntervalSchedule, PeriodicTask

from django_napse.core.celery_app import celery_app, strategy_log_free


class BaseTask(celery.Task):
    """Base class for all Celery tasks."""

    name = "base_task"
    Strategy = strategy_log_free
    logger = get_task_logger(name)
    interval_time = 5  # Impossible to make dynamic modification because of celery

    def __init__(self) -> None:
        super().__init__()
        self.logger.setLevel("INFO")

    def run(self) -> None:
        """Function called when running the task."""

    def info(self, msg: str) -> None:
        """Log a message."""
        info = f"[{self.name} @{datetime.now(tz=timezone.utc)}] : {msg}"
        self.logger.info(info)

    def error(self, msg: str) -> None:
        """Log an error."""
        error = f"[{self.name} @{datetime.now(tz=timezone.utc)}] : {msg}"
        self.logger.error(error)

    def warning(self, msg: str) -> None:
        """Log a warning."""
        warning = f"[{self.name} @{datetime.now(tz=timezone.utc)}] : {msg}"
        self.logger.warning(warning)

    def create_task(self) -> None:
        """Build task feed_bots_with_candles.

        Raises:
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
            info = f"Period task {self.name} created"
            self.info(info)
        except IntegrityError:
            pass

    def delete_task(self) -> None:
        """Remove task from database.

        Raises:
            ValidationError: if task doesn't exist
        """
        try:
            PeriodicTask.objects.get(task=self.name).delete()
            info = f"Period task {self.name} deleted"
            self.info(info)
        except PeriodicTask.DoesNotExist:
            pass
        except ProgrammingError:
            pass

    def register_task(self) -> None:
        """Register task to database."""
        celery_app.register_task(self)
        self.create_task()
        info = f"Period task {self.name} registered"
        self.info(info)

    def active_tasks(self) -> dict:
        """Return active tasks."""
        return celery_app.control.inspect().active()

    def num_active_tasks(self) -> int:
        """Return number of active tasks."""
        active_tasks = self.active_tasks()
        count = 0
        for worker in active_tasks:
            for task in active_tasks[worker]:
                if task["name"] == self.name:
                    count += 1
        return count

    def avoid_overlap(self, *, verbose: Optional[bool] = False) -> bool:
        """Avoid task overlap.

        Args:
            verbose (bool, optional): Whether to print logs. Defaults to False.

        Returns:
            bool: True if task is not running, False otherwise
        """
        if self.num_active_tasks() > 1:
            if verbose:
                info = f"Period task {self.name} already running"
                self.info(info)
            return False
        return True
