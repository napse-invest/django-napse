import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.test_app.settings")

from django_napse.core.celery_app import celery_app  # noqa
