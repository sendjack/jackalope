#!/usr/bin/env python
"""
    Jackalope Service Poller
    ------------------------

    Run Jackalope on a regular interval to poll for work (new and updates
    tasks; comments.)

"""

from apscheduler.scheduler import Scheduler

from jutil import environment
from foreman import Foreman

INTERVAL_SECONDS = unicode("INTERVAL_SECONDS")
sched = Scheduler()
interval = environment.get_integer(INTERVAL_SECONDS)
# actually_running: fulfills ApScheduler True requirement and doesn't loop
# indefintiely while Sphinx generates documentation.
actually_running = environment.get_integer(INTERVAL_SECONDS)


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
