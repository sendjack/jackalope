"""
    DB Worker
    ---------

    DB Worker converts data from our database into Jackalope objects and vice
    versa.

    NOTE: This class is intended to subclass from VendorWorker as there are a
    lot of similarities between the vendor workers and the db worker, but that
    is for another day.

"""

from jackalope.util.decorators import constant
from jackalope.data.db import db


class _JackField(object):

    """Constants for the database dictionary fields."""

    @constant
    def VENDOR_TASK_ID(self):
        return "vendor_task_id"

    @constant
    def VENDOR_NAME(self):
        return "vendor_name"

    @constant
    def TASK_ID(self):
        return "task_id"

    @constant
    def RECIPROCAL_VENDOR_TASK_ID(self):
        return "reciprocal_vendor_task_id"

    @constant
    def RECIPROCAL_VENDOR_NAME(self):
        return "reciprocal_vendor_name"

    @constant
    def SYNCHED_TS(self):
        return "synched_ts"

JACK_FIELD = _JackField()


class DbWorker(object):

    """Interface between the database and the Jackalope objects."""


    def __init__(self):
        self._vendor_tasks_table = db.vendor_tasks


    def does_task_exist(self, vendor_task_id, vendor_name):
        result_dict = self._vendor_tasks_table.read_by_pk(
                unicode(vendor_task_id),
                unicode(vendor_name))

        task_id = None
        vendor_name = None
        if result_dict:
            task_id = result_dict.get(
                    JACK_FIELD.VENDOR_TASK_ID)
            vendor_name = result_dict.get(
                    JACK_FIELD.VENDOR_NAME)

        return task_id is not None and vendor_name is not None


    def get_reciprocal_task_info(self, vendor_task_id, vendor_name):
        result_dict = self._vendor_tasks_table.read_by_pk(
                unicode(vendor_task_id),
                unicode(vendor_name))

        reciprocal_task_id = None
        reciprocal_vendor_name = None
        if result_dict:
            reciprocal_task_id = result_dict.get(
                    JACK_FIELD.RECIPROCAL_VENDOR_TASK_ID)
            reciprocal_vendor_name = result_dict.get(
                    JACK_FIELD.RECIPROCAL_VENDOR_NAME)

        print "RESULT", result_dict
        return (reciprocal_task_id, reciprocal_vendor_name)


    def create_vendor_task(
            self,
            vendor_task_id,
            vendor_name,
            synched_ts,
            reciprocal_task_id,
            reciprocal_vendor_name):
        properties = {
                JACK_FIELD.VENDOR_TASK_ID: unicode(vendor_task_id),
                JACK_FIELD.VENDOR_NAME: unicode(vendor_name),
                JACK_FIELD.SYNCHED_TS: synched_ts,
                }

        # TODO: XXX XXX
        result = self._vendor_tasks_table.create(properties)
        print result

        return result
