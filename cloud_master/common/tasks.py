"""
from __future__ import absolute_import, unicode_literals

import time
from celery.result import allow_join_result
from common.scheduler import cloud_task, async_do_job


### usage:

# if you don't care function's result, set (ignore_result=True) to improve performance.
@cloud_task
def add(a, b):
    return a + b


tasks.add(4,6) --> run directly

tasks.add.delay(3,4) --> run in celery worker

tasks.add.delay(3, 4, language="fr", storage_config=None) --> run in celery worker with language "fr"

async_do_job(tasks.add, 3, 4) --> run in celery worker switch language and hybrid cloud db auto

t=tasks.add.delay(3,4) --> t.get()  get result or block

t.ready() --> False：not done yet，True：done

t.get(propagate=False) --> get result, if error occur, raise Exception

t.traceback --> get traceback string



### advanced usage:

@cloud_task
def t1():
    time.sleep(5)
    return 123


@cloud_task
def t2():
    time.sleep(7)
    return 456

# no decorator here
def t3():
    t11 = t1.delay()
    t22 = t2.delay()
    return t11.get() + t22.get()

@cloud_task
def t4():
    with allow_join_result():
        t11 = t1.delay()
        t22 = t2.delay()
        return t11.get() + t22.get()

t3() -->  block 7s and get the result

ret = t4.delay() --> the worker running behind block 7s
--> do something else
ret.get() --> get the result



### how to run celery?

local:
    celery -A cloud worker -l info -B -Q beat,celery

online server:
    celery -A cloud worker -l info -Q beat,celery
    celery -A cloud beat -S redbeat.RedBeatScheduler

"""
