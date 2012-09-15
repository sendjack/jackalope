""" Module: asana_requester

All functions for interacting with Asana.

"""
# ran ./setup.py on pandemicsyn / asana
import xml.etree.cElementTree as ET
from asana import asana

import settings

from requester import Requester, Task


FIELD_TYPE = "asana"
FIELD_ID = "id"
FIELD_NAME = "name"
FIELD_PRICE = "price"
FIELD_NOTES = "notes"


class AsanaRequester(Requester):

    """ Connect with Asana to allow requests.

    Required:
    AsanaAPI _asana_api     a connection to the asana api
    dict _workspaces        all the user's workspaces, keyed on id

    """


    def __init__(self):
        """ Construct AsanaRequester. """
        self._asana_api = asana.AsanaAPI(
                settings.ASANA_API_KEY,
                debug=True)
        self._workspaces = AsanaRequester.produce_dict(
                self._asana_api.list_workspaces())


    def get_tasks(self):
        """ Return the Tasks that will be done. """
        test_workspace_id = AsanaRequester.retrieve_id(
                self._workspaces.get(settings.TEST_WORKSPACE_ID))

        tags = AsanaRequester.produce_dict(
                self._asana_api.get_tags(test_workspace_id))

        test_tag_id = AsanaRequester.retrieve_id(
                tags.get(settings.JACKALOPE_TAG_ID))

        short_tasks = AsanaRequester.produce_dict(
                self._asana_api.get_tag_tasks(test_tag_id))

        tasks = []
        for task_id in short_tasks.keys():
            tasks.append(AsanaTask(self._asana_api.get_task(task_id)))

        return {t.id: t for t in tasks}


    @staticmethod
    def retrieve_id(asana_object):
        """ Get the ID from the asana_object. """
        return asana_object[FIELD_ID]


    @staticmethod
    def produce_dict(asana_list):
        """ Convert the list into a dict keyed on ID. """
        return {AsanaRequester.retrieve_id(a): a for a in asana_list}


class AsanaTask(Task):

    """ Construct a Task using Asana task data.

    Required:
    str _type           Requester type.
    id _id              The id of the task, pulled from the source.
    str _name           The name of the task, pulled from the source.
    int _price          The price of the task in US Dollars.

    Optional:
    str _description    Task description

    """


    def _construct_task(self, proto_task):
        """ Construct Task.

        Required:
        dict proto_task     The raw task from the data source.

        """
        asana_task = proto_task  # accessing asana specific fields

        # set required  mapped fields
        self._type = FIELD_TYPE
        self._id = asana_task[FIELD_ID]
        self._name = asana_task[FIELD_NAME]

        # set required embedded fields
        self._price = AsanaTask._extract_field(asana_task, FIELD_PRICE)

        # set optional mapped fields
        self._description = AsanaTask._extract_description(asana_task)

        # set optional embedded fields


    @staticmethod
    def _extract_description(asana_task):
        """ Use the "notes" field but remove the embedded content. """
        xml_blob = AsanaTask._convert_field_to_xml(asana_task.get(FIELD_NOTES))
        return ET.XML(xml_blob).text.strip()


    @staticmethod
    def _extract_field(asana_task, field):
        """ Extract the embedded field in "notes" and return it. """
        xml_blob = AsanaTask._convert_field_to_xml(asana_task.get(FIELD_NOTES))
        elem = ET.XML(xml_blob)
        return elem.find(field).text.strip()


    @staticmethod
    def _convert_field_to_xml(field):
        """ Converts a field to xml by wrapping it in xml tags. """
        return "<blob>{}</blob>".format(field)
