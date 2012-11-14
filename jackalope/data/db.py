"""

    db
    --

    Database singleton.

"""

from postgres import Postgres


class _DatabseSingleton(object):


    def __init__(self):
        self._db = Postgres()


    @property
    def db(self):
        return self._db


db = _DatabseSingleton().db
