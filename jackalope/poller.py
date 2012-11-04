#!/usr/bin/env python
"""
    Jackalope Service Poller
    ------------------------

    Run Jackalope on a regular interval to poll for work (new and updates
    tasks; comments.)

"""

import os
from apscheduler.scheduler import Scheduler

from foreman import Foreman
from util import integer


sched = Scheduler()
interval = integer.to_integer(os.environ.get("INTERVAL_SECONDS", 10000))
# actually_running: fulfills ApScheduler True requirement and doesn't loop
# indefintiely while Sphinx generates documentation.
actually_running = os.environ.get("INTERVAL_SECONDS")


@sched.interval_schedule(seconds=interval)
def timed_job():
    """Call the app.py main method."""
    print "Polling commence..."
    foreman = Foreman()
    foreman.send_jack()
    print "...Polling complete.\n\n\n\n"


sched.start()


# required by ApScheduler
while actually_running:
    pass
