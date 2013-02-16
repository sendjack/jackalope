"""

    database
    --------

    Generic database object.

"""

from jutil.errors import OverrideRequiredError


class Database(object):


    def __init__(self):
        self._connect()
        self._create_cursor()
        self._load_tables()


    def _connect(self):
        raise OverrideRequiredError()


    def _create_cursor(self):
        raise OverrideRequiredError()


    def _load_tables(self):
        raise OverrideRequiredError()
