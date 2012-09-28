#!/usr/bin/env python
""" Module: clock

A wrapper around the app to run it on a schedule.

"""
import os
from apscheduler.scheduler import Scheduler

import app


sched = Scheduler()
interval = int(os.environ.get("INTERVAL_SECONDS"))


@sched.interval_schedule(seconds=interval)
def timed_job():
    """ Call the app.py main method. """
    print "and another job..."
    app.main()

sched.start()


# required by ApScheduler
while True:
    pass
