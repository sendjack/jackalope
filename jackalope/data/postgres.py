"""
    postgres
    --------

    Postgres is our implementation of Python's DB-API using psycopg2 to fetch
    data from a PostgreSQL database.

    Notes
    +++++

    See:
    http://www.python.org/dev/peps/pep-0249/
    http://www.initd.org/psycopg/
    http://www.initd.org/psycopg/docs/
    http://wiki.postgresql.org/wiki/Using_psycopg2_with_PostgreSQL
    https://postgres.heroku.com/databases/jackalope-charcoal
    http://stackoverflow.com/questions/10640532/python-database-without-using-
        django-for-heroku

"""

import psycopg2

from util.decorators import constant
from util import environment

from database import Database
from vendor_tasks import VENDOR_TASKS, VendorTasksTable
#from tasks import TASKS, TasksTable


class _Postgres(object):

    @constant
    def URL(self):
        return environment.get_unicode("DATABASE_URL")

    @constant
    def HOST(self):
        return environment.get_unicode("PGHOST")

    @constant
    def PORT(self):
        return environment.get_integer("PGPORT")

    @constant
    def DATABASE(self):
        return environment.get_unicode("PGDATABASE")

    @constant
    def USER(self):
        return environment.get_unicode("PGUSER")

    @constant
    def PASSWORD(self):
        return environment.get_unicode("PGPASSWORD")

POSTGRES = _Postgres()


class Postgres(Database):


    def _connect(self):
        #self._connection = psycopg2.connect()

        # TODO: check whether we need these arguments
        self._connection = psycopg2.connect(
                host=POSTGRES.HOST,
                port=POSTGRES.PORT,
                database=POSTGRES.DATABASE,
                user=POSTGRES.USER,
                password=POSTGRES.PASSWORD)


    def _create_cursor(self):
        self._cursor = self._connection.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor)


    def _load_tables(self):
        self._tables = {
                VENDOR_TASKS.NAME: VendorTasksTable(self._cursor),
                #TASKS.NAME: TasksTable(self._cursor),
                }


    @property
    def vendor_tasks(self):
        return self._tables.get(VENDOR_TASKS.NAME)


    #@property
    #def tasks(self):
    #    return self._tables.get(TASKS.NAME)
