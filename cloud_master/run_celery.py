import threading
import time

from cloud.celery import app

"""
This script is only for development environment to debug.
run path: yuyi_cloud2/cloud_master
You can also execute following command on local:
    celery -A cloud worker -l info -B -Q beat,celery
But the production server should use the following command:
    celery -A cloud worker -l info -Q beat,celery
    celery -A cloud beat -S redbeat.RedBeatScheduler
"""


def run_beat():
    app.Beat(loglevel="DEBUG").run()


def run_worker():
    args = ("worker", "-A", "cloud", "-l", "DEBUG", "-Q", "beat,celery")
    app.Worker(loglevel="DEBUG", argv=args).start()


if __name__ == "__main__":
    t = threading.Thread(target=run_beat)
    t.start()
    time.sleep(18)
    run_worker()
