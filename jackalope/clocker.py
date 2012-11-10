import os
from threading import Timer

from foreman import Foreman
from util import integer


interval = integer.to_integer(os.environ.get("INTERVAL_SECONDS", 10000))


def timed_job():
    """Call the app.py main method."""
    print "Polling commence..."
    foreman = Foreman()
    foreman.send_jack()
    print "...Polling complete.\n\n\n\n"

    Timer(interval, timed_job).start()

timed_job()
