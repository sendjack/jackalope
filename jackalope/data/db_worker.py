"""
    DB Worker
    ---------

    DB Worker converts data from our database into Jackalope objects and vice
    versa.

    NOTE: This class is intended to subclass from VendorWorker as there are a
    lot of similarities between the vendor workers and the db worker, but that
    is for another day.

"""

from jutil.decorators import constant
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

        task_exists = False
        if result_dict:
            task_exists = all([
                    result_dict.get(JACK_FIELD.VENDOR_TASK_ID),
                    result_dict.get(JACK_FIELD.VENDOR_NAME)
                    ])

        return task_exists


    def get_reciprocal_task_info(self, vendor_task_id, vendor_name):
        result_dict = self._vendor_tasks_table.read_by_pk(
                vendor_task_id,
                vendor_name)

        reciprocal_task_id = None
        reciprocal_vendor_name = None
        if result_dict:
            reciprocal_task_id = result_dict.get(
                    JACK_FIELD.RECIPROCAL_VENDOR_TASK_ID)
            reciprocal_vendor_name = result_dict.get(
                    JACK_FIELD.RECIPROCAL_VENDOR_NAME)

        return (reciprocal_task_id, reciprocal_vendor_name)


    def get_synched_ts(self, vendor_task_id, vendor_name):
        result_dict = self._vendor_tasks_table.read_by_pk(
                vendor_task_id,
                vendor_name)

        synched_ts = None
        if result_dict:
            synched_ts = result_dict.get(JACK_FIELD.SYNCHED_TS)

        return synched_ts

    def create_vendor_task(
            self,
            vendor_task_id,
            vendor_name,
            synched_ts,
            reciprocal_task_id,
            reciprocal_vendor_name):
        properties = {
                JACK_FIELD.VENDOR_TASK_ID: vendor_task_id,
                JACK_FIELD.VENDOR_NAME: vendor_name,
                JACK_FIELD.SYNCHED_TS: synched_ts,
                JACK_FIELD.RECIPROCAL_VENDOR_TASK_ID: reciprocal_task_id,
                JACK_FIELD.RECIPROCAL_VENDOR_NAME: reciprocal_vendor_name
                }

        return self._vendor_tasks_table.create(properties)


    def update_vendor_synched_ts(
            self,
            vendor_task_id,
            vendor_name,
            synched_ts):
        properties = {
                JACK_FIELD.SYNCHED_TS: synched_ts
                }

        return self._vendor_tasks_table.update_by_pk(
                vendor_task_id,
                vendor_name,
                properties)


#update_reciprocal_vendor_task_pk(reciprocal_vendor_task_pk)
#get_vendor_name(vendor_task_id)
