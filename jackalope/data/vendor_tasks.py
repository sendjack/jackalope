"""

    vendor_tasks
    ------------

    CREATE TABLE vendor_tasks (
        vendor_task_id VARCHAR(32),
        vendor_name VARCHAR(32),
        task_id INTEGER,
        reciprocal_vendor_task_id VARCHAR(32),
        reciprocal_vendor_name VARCHAR(32),
        synched_ts INTEGER,
        created_ts INTEGER,
        updated_ts INTEGER,
        deleted_ts INTEGER,
        PRIMARY KEY (vendor_task_id, vendor_name)
    );

"""

from jutil.decorators import constant

from table import _Table, Table


class _VendorTasksTable(_Table):

    @constant
    def NAME(self):
        return "vendor_tasks"

    @constant
    def COLUMNS(self):
        return [
                "vendor_task_id",
                "vendor_name",
                "task_id",
                "reciprocal_vendor_task_id",
                "reciprocal_vendor_name",
                "synched_ts",
                "created_ts",
                "updated_ts",
                "deleted_ts",
                ]

    @constant
    def PRIMARY_KEY(self):
        return [
                "vendor_task_id",
                "vendor_name",
                ]

    @constant
    def UNIQUE_KEYS(self):
        # TODO: FILL THIS IN (BUT ONLY IF IT'S NEEDED)!
        return []

    @constant
    def FOREIGN_KEYS(self):
        # TODO: FILL THIS IN (BUT ONLY IF IT'S NEEDED)!
        return []

VENDOR_TASKS = _VendorTasksTable()



class VendorTasksTable(Table):

    def __init__(self, cursor):
        super(VendorTasksTable, self).__init__(
                VENDOR_TASKS.NAME,
                VENDOR_TASKS.COLUMNS,
                VENDOR_TASKS.PRIMARY_KEY,
                cursor)

        # definitely never change this. ever. this table has no autoincrement
        # primary key, and this is how we explicitly notify the superclass.
        self._use_auto_key(False)

        # uncomment these if they turn out to be needed
        #self._set_unique_keys(VENDOR_TASKS.UNIQUE_KEYS)
        #self._set_foreign_keys(VENDOR_TASKS.FOREIGN_KEYS)


    def _primary_key_properties(self, vendor_task_id, vendor_name):
        # TODO: is this a hackjob? how can it be better?
        return {
                VENDOR_TASKS.PRIMARY_KEY[0]: vendor_task_id,
                VENDOR_TASKS.PRIMARY_KEY[1]: vendor_name,
                }


    def create(self, properties):
        return self._create_row(properties)


    def create_or_update_by_pk(self, vendor_task_id, vendor_name, properties):
        pk = self._primary_key_properties(vendor_task_id, vendor_name)
        return self._create_or_update_row(pk, properties)


    def read_by_pk(self, vendor_task_id, vendor_name):
        pk = self._primary_key_properties(vendor_task_id, vendor_name)
        return self._read_row(pk)


    def update_by_pk(self, vendor_task_id, vendor_name, properties):
        pk = self._primary_key_properties(vendor_task_id, vendor_name)
        return self._update_row(pk, properties)


    def delete_by_pk(self, vendor_task_id, vendor_name):
        pk = self._primary_key_properties(vendor_task_id, vendor_name)
        return self._delete_row(pk)
