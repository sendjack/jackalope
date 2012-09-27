""" Module: asana_employer

AsanaEmployer subclasses Employer and handles all interaction between Jackalope
and Asana.

"""
# ran ./setup.py on pandemicsyn / asana
import xml.etree.cElementTree as ET
from asana import asana

import settings
from task import Task

from base import Employer

FIELD_SERVICE = "asana"
FIELD_ID = "id"
FIELD_NAME = "name"
FIELD_PRICE = "price"
FIELD_NOTES = "notes"


class AsanaEmployer(Employer):

    """ Connect with Asana to allow requests.

    Required:
    AsanaAPI _asana_api     a connection to the asana api
    dict _workspaces        all the user's workspaces, keyed on id

    """


    def __init__(self):
        """ Construct AsanaEmployer. """
        self._asana_api = asana.AsanaAPI(
                settings.ASANA_API_KEY,
                debug=True)
        self._workspaces = self._produce_dict(
                self._asana_api.list_workspaces())


    def read_task(self, task_id):
        """ Connect to Worker's service and return the requested Task."""
        # FIXME: implement
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)


    def read_tasks(self):
        """ Connect to Worker's service and return all tasks.

        Return:
        dict    all the Tasks keyed on id

        """
        test_workspace_id = AsanaEmployer._retrieve_id(
                self._workspaces.get(settings.TEST_WORKSPACE_ID))

        tags = self._produce_dict(
                self._asana_api.get_tags(test_workspace_id))

        test_tag_id = AsanaEmployer._retrieve_id(
                tags.get(settings.JACKALOPE_TAG_ID))

        short_asana_tasks = self._produce_dict(
                self._asana_api.get_tag_tasks(test_tag_id))

        tasks = {}
        for asana_task_id in short_asana_tasks.keys():
            task = self._construct_task(
                    self._asana_api.get_task(asana_task_id))
            tasks[task.id] = task

        return tasks


    def _construct_task(self, raw_task):
        """ Construct Task from the raw task.

        Required:
        dict raw_task       The raw task from the data source.

        Return:
        Task The Task built from the raw task.

        """
        asana_task = raw_task  # accessing asana specific fields

        # get required  mapped fields
        service = FIELD_SERVICE
        id = asana_task[FIELD_ID]
        name = asana_task[FIELD_NAME]

        # get required embedded fields
        price = AsanaEmployer._extract_field(asana_task, FIELD_PRICE)

        # get optional mapped fields
        description = AsanaEmployer._extract_description(asana_task)

        # get optional embedded fields

        task = Task(id, service, name, price)
        task.set_description(description)

        return task


    @staticmethod
    def _extract_description(asana_task):
        """ Use the "notes" field but remove the embedded content. """
        return AsanaEmployer._extract_field(asana_task)


    @staticmethod
    def _extract_field(asana_task, field=None):
        """ Extract the embedded field in "notes" and return it. """
        notes = asana_task.get(FIELD_NOTES)
        xml_blob = AsanaEmployer._convert_field_to_xml(notes)
        elem = ET.XML(xml_blob)
        text = elem.text if field is None else elem.find(field).text
        return text.strip() if text else ""


    @staticmethod
    def _convert_field_to_xml(field):
        """ Converts a field to xml by wrapping it in xml tags. """
        return "<blob>{}</blob>".format(field)


    @staticmethod
    def _retrieve_id(raw_task):
        """ Get the 'id' from the raw task. """
        asana_task = raw_task  # need to access asana fields.
        return asana_task[FIELD_ID]
