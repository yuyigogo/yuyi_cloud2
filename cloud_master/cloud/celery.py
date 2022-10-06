from __future__ import absolute_import, unicode_literals

import logging
import os
import ssl

from celery import Celery
from celery.schedules import crontab
from celery.signals import before_task_publish
from django.conf import settings


logger = logging.getLogger(__name__)


# set the default Django settings module for the 'celery' program.
SETTINGS = "cloud.settings"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", SETTINGS)

query_kwargs = {"redbeat_redis_url": settings.CELERY_REDBEAT_REDIS_URL}

if settings.CELERY_REDBEAT_REDIS_URL.startswith("rediss://"):
    query_kwargs["redis_backend_use_ssl"] = {"ssl_cert_reqs": ssl.CERT_NONE}

app = Celery("cloud_master", **query_kwargs)


# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# crontab usage:
# https://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html#crontab-schedules
#
# make sure all periodic task have a specified queue, so we call split delay task and periodic task.
# now use "beat" as periodic task's queue name.
# if we add another queue, tell develop to start the new queue.

app.conf.beat_schedule = {
    # "add-every-10-seconds": {
    # "task": "gin2.celery.test",
    # "schedule": 10,
    # "args": None,
    # "options": {"queue": "beat"},
    # },
    # "add-every-minute": {
    # "task": "contract.tasks.add",
    # "schedule": crontab(minute="*"),
    # "args": (16, 27),
    # "options": {"queue": "beat"},
    # },
    "async_customer_status_statistic": {
        "task": "cloud_home.tasks.async_customer_status_statistic",
        "schedule": crontab(minute=0, hour=1),
        "args": None,
        "options": {"queue": "beat"},
    },
    "async_site_status_statistic": {
        "task": "cloud_home.tasks.async_site_status_statistic",
        "schedule": crontab(minute=0, hour=1),
        "args": None,
        "options": {"queue": "beat"},
    },
    "async_customer_equipment_abnormal_ratio": {
        "task": "cloud_home.tasks.async_customer_equipment_abnormal_ratio",
        "schedule": crontab(hour=0, minute=1),
        "args": None,
        "options": {"queue": "beat"},
    },
    "async_site_equipment_abnormal_ratio": {
        "task": "cloud_home.tasks.async_site_equipment_abnormal_ratio",
        "schedule": crontab(hour=0, minute=3),
        "args": None,
        "options": {"queue": "beat"},
    },
}

# celery-once config
app.conf.ONCE = {
    "backend": "celery_once.backends.Redis",
    "settings": {
        "url": f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/2",
        "default_timeout": 60 * 60,
    },
}


@before_task_publish.connect
def task_send_handler(sender=None, headers=None, body=None, **kwargs):
    """
    :param sender: 'contract.tasks.test_task'
    :param headers: {'lang': 'py',
                     'task': 'contract.tasks.test_task',
                     'id': 'faf603bb-f8bc-4ab4-91fe-ea29f5910ecc',
                     'shadow': None,
                     'eta': None,
                     'expires': None,
                     'group': None,
                     'group_index': None,
                     'retries': 0,
                     'timelimit': [None, None],
                     'root_id': 'faf603bb-f8bc-4ab4-91fe-ea29f5910ecc',
                     'parent_id': None,
                     'argsrepr': '(1, 2)',
                     'kwargsrepr': '{}',
                     'origin': 'gen60197@icedeMacBook-Pro.local',
                     'ignore_result': False}
    :param body: ((1, 2), {}, {'callbacks': None, 'errbacks': None, 'chain': None, 'chord': None})
    :param kwargs: {'signal': <Signal: before_task_publish providing_args={'headers', 'body', 'exchange', 'retry_policy', 'properties', 'declare', 'routing_key'}>,
                    'exchange': '',
                    'routing_key': 'celery',
                    'declare': [<unbound Queue celery -> <unbound Exchange celery(direct)> -> celery>],
                    'properties': {'correlation_id': faf603bb-f8bc-4ab4-91fe-ea29f5910ecc',
                                    'reply_to': '63876df8-4dbd-3725-85f1-f08a4c521a5c'
                                    },
                    'retry_policy': None
                    }
    :return:
    """
    try:
        args, *_ = body
        limited_args = [
            arg[:100] if isinstance(arg, (bytes, str)) else arg for arg in args
        ]
        logger.info(f"task: {sender}({headers['id']}), args: {limited_args}")
    except Exception as e:
        logger.exception(f"task_send_handler error: {headers=}, {body=}, {kwargs=} {e}")
