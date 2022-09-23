import base64
import logging
import pickle
import traceback
from functools import wraps

from celery import shared_task
from celery_once import QueueOnce
from cloud.celery import app

logger = logging.getLogger(__name__)


def async_do_job(task, *args, **kwargs):
    logger.info(f"send_task: {task.name}")
    return app.send_task(task.name, args=args, kwargs=kwargs)


def task_handle(func, *args, **kwargs):
    try:
        result = func(*args, **kwargs)
        return result
    except Exception as e:
        traceback_msg = traceback.format_exc()
        logger.error(traceback_msg)


def double_wrap(decorator):
    """
    A decorator decorator, allowing the decorator to be used as:
    @decorator(with, arguments, and=kwargs)
    or
    @decorator
    """

    @wraps(decorator)
    def new_dec(*task_args, **task_kwargs):
        if len(task_args) == 1 and len(task_kwargs) == 0 and callable(task_args[0]):
            return decorator(task_args[0])
        else:
            run_lock = task_kwargs.pop("run_lock", True)
            if run_lock is True:
                task_kwargs.setdefault("base", QueueOnce)
                task_kwargs.setdefault("once", {"graceful": True})
            return lambda real_decorator: decorator(
                real_decorator, *task_args, **task_kwargs
            )

    return new_dec


@double_wrap
def cloud_task(func, *task_args, **task_kwargs):
    @shared_task(*task_args, **task_kwargs)
    @wraps(func)
    def wrapper(*args, **kwargs):
        return task_handle(func, *args, **kwargs)

    return wrapper


def async_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return async_do_job(func, *args, **kwargs)

    return wrapper


def dumps(obj):
    data = pickle.dumps(obj)
    return base64.b64encode(data).decode()


def loads(encoded):
    data = base64.b64decode(encoded)
    return pickle.loads(data)
