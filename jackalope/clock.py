#!/usr/bin/env python
"""
    clock
    -----

    A wrapper around the app to run it on a schedule.

"""

import os
from apscheduler.scheduler import Scheduler

import app
from util import integer


sched = Scheduler()
interval = integer.to_integer(os.environ.get("INTERVAL_SECONDS", 10000))
actually_running = os.environ.get("INTERVAL_SECONDS")


@sched.interval_schedule(seconds=interval)
def timed_job():
    """Call the app.py main method."""
    print "and another job..."
    app.main()


sched.start()


# required by ApScheduler
while actually_running:
    pass
