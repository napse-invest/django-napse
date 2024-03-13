from datetime import datetime, timezone
from time import sleep, time

import celery
import redis
from celery.app.task import ExceptionInfo
from celery.utils.log import get_task_logger
from django.conf import settings
from django.db import IntegrityError
from django.db.utils import ProgrammingError
from django_celery_beat.models import IntervalSchedule, PeriodicTask

from django_napse.core.celery_app import celery_app, strategy_log_free

redis_client = redis.Redis(host=settings.CELERY_BROKER_URL.split("//")[1].split(":")[0], port=settings.CELERY_BROKER_URL.split(":")[2].split("/")[0])


class BaseTask(celery.Task):
    """Base class for all Celery tasks."""

    name = "base_task"
    Strategy = strategy_log_free
    logger = get_task_logger("django")
    interval_time = 5  # Impossible to make dynamic modification because of celery
    min_interval_time = 4

    def __init__(self) -> None:
        super().__init__()
        if self.min_interval_time > self.interval_time:
            error_msg = f"min_interval_time ({self.min_interval_time}) must be lower than interval_time ({self.interval_time})"
            raise ValueError(error_msg)
        self.logger.setLevel("INFO")

    def run(self) -> None:
        """Function called when running the task."""
        t = time()
        redis_client.set(self.name, t, nx=True, ex=self.interval_time + 1)
        lock = redis_client.get(self.name)
        if lock is None or lock.decode("utf-8") != str(t):
            return
        self._run()
        sleep(self.min_interval_time)  # let all the other tasks fail
        redis_client.delete(self.name)

    def _run(self) -> None:
        """Run the task."""

    def info(self, msg: str) -> None:
        """Log a message."""
        info = f"[{datetime.now(tz=timezone.utc)} @{self.name}] : {msg}"
        self.logger.info(info)

    def error(self, msg: str) -> None:
        """Log an error."""
        error = f"[{datetime.now(tz=timezone.utc)} @{self.name}] : {msg}"
        self.logger.error(error)

    def warning(self, msg: str) -> None:
        """Log a warning."""
        warning = f"[{datetime.now(tz=timezone.utc)} @{self.name}] : {msg}"
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

    def on_failure(self, exc: Exception, task_id: str, args: tuple, kwargs: dict, einfo: ExceptionInfo) -> None:  # noqa: ARG002
        """Error handler.

        This is run by the worker when the task fails.

        Arguments:
            exc (Exception): The exception raised by the task.
            task_id (str): Unique id of the failed task.
            args (Tuple): Original arguments for the task that failed.
            kwargs (Dict): Original keyword arguments for the task that failed.
            einfo (~billiard.einfo.ExceptionInfo): Exception information.

        Returns:
            None: The return value of this handler is ignored.
        """
        """Log error on failure."""
        error = f"[{self.name} @{datetime.now(tz=timezone.utc)}] : {exc}"
        self.error(error)
        self.error(einfo)
