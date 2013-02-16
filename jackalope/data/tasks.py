"""

    tasks
    -----

"""

from jutil.decorators import constant

from table import Table


class _TasksTable(object):

    @constant
    def NAME(self):
        return "tasks"

    @constant
    def COLUMNS(self):
        return [
                "task_id",
                "status",
                "category",
                "price",
                "description",
                "created_ts",
                "updated_ts",
                "deleted_ts",
                ]

    @constant
    def PRIMARY_KEY(self):
        return [
                "task_id",
                ]

    @constant
    def UNIQUE_KEYS(self):
        # TODO: FILL THIS IN (BUT ONLY IF IT'S NEEDED)!
        return []

    @constant
    def FOREIGN_KEYS(self):
        # TODO: FILL THIS IN (BUT ONLY IF IT'S NEEDED)!
        return []

TASKS = _TasksTable()


class TasksTable(Table):


    def __init__(self, cursor):
        super(TasksTable, self).__init__(
                TASKS.NAME,
                TASKS.COLUMNS,
                TASKS.PRIMARY_KEY,
                cursor)

        # definitely never change this. ever. this table has an autoincrement
        # primary key, and this is how we explicitly notify the superclass.
        self._use_auto_key(True)

        # uncomment these if they turn out to be needed
        #self._set_unique_keys(VENDOR_TASKS.UNIQUE_KEYS)
        #self._set_foreign_keys(VENDOR_TASKS.FOREIGN_KEYS)


    def _primary_key_properties(self, task_id):
        # TODO: is this a hackjob? how can it be better?
        return {
                TASKS.PRIMARY_KEY[0]: task_id,
                }


    def create(self, properties):
        return self._create_row(properties)


    def create_or_update_by_pk(self, task_id, properties):
        pk = self._primary_key_properties(task_id)
        return self._create_or_update_row(pk, properties)


    def read_by_pk(self, task_id):
        pk = self._primary_key_properties(task_id)
        return self._read_row(pk)


    def update_by_pk(self, task_id, properties):
        pk = self._primary_key_properties(task_id)
        return self._update_row(pk, properties)


    def delete_by_pk(self, task_id):
        pk = self._primary_key_properties(task_id)
        return self._delete_row(pk)
