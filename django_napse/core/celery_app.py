import os
from unittest import mock

import celery
from celery.app import trace
from celery.signals import setup_logging
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.test_app.settings")
celery_app = celery.Celery("django_napse")


# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
celery_app.config_from_object(settings, namespace="CELERY")

# Gestion des logs ------------------------------------------------------------------
# Remove the trace from celery logs
old_info = trace.info
trace.info = mock.Mock()


# Configure celery logging
@setup_logging.connect
def config_loggers(*args: list, **kwargs: dict) -> None:  # noqa: ARG001
    """Take settings.LOGGING as config for celery loggers (especially for `formatters`)."""
    from logging.config import dictConfig

    from django.conf import settings

    dictConfig(settings.LOGGING)


# Remove the strategy from celery logs
def strategy_log_free(*args: list, **kwargs: dict) -> callable:
    """Remove the strategy from celery logs."""
    kwargs["info"] = mock.Mock()
    return celery.worker.strategy.default(*args[1:], **kwargs)


# Load task modules from all registered Django app configs.
celery_app.autodiscover_tasks()
