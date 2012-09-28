""" Module: asana_employer

AsanaEmployer subclasses Employer and handles all interaction between Jackalope
and Asana.

"""
# ran ./setup.py on pandemicsyn / asana
import xml.etree.cElementTree as ET
from asana import asana

from util.decorators import constant
import settings

from base import Employer


class _Field(object):

    """ The ServiceWorker's field constants for interacting with the
    services. """

    @constant
    def ID(self):
        return "id"

    @constant
    def NAME(self):
        return "name"

    @constant
    def PRICE(self):
        return "price"

    @constant
    def DESCRIPTION(self):
        return "description"

    @constant
    def NOTES(self):
        return "notes"

FIELD = _Field()


class AsanaEmployer(Employer):

    """ Connect with Asana to allow requests.

    Required:
    str _embedding_field        The field to use to embed other fields.
    AsanaAPI _asana_api     a connection to the asana api
    dict _workspaces        all the user's workspaces, keyed on id

    """

    SERVICE = "asana"


    def __init__(self):
        """ Construct AsanaEmployer. """
        self._embedding_field = FIELD.NOTES
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


    def _extract_from_embedding_field(self, asana_task):
        """ Remove the embedded content. """
        fields = {}

        fields[FIELD.DESCRIPTION] = self._extract_field(asana_task)
        fields[FIELD.PRICE] = self._extract_field(
                asana_task,
                FIELD.PRICE)

        return fields


    def _extract_field(self, asana_task, field=None):
        """ Extract the embedded field and return it. """
        notes = asana_task.get(self._embedding_field)
        xml_blob = AsanaEmployer._convert_field_to_xml(notes)
        elem = ET.XML(xml_blob)
        text = elem.text if field is None else elem.find(field).text
        return text.strip() if text else ""


    @staticmethod
    def _extract_required_fields(raw_task):
        """ Remove the required fields from the raw_task dict and return them.

        Required:
        dict raw_task       The raw task dictionary.

        Return:
        tuple (id, str) - return the the (id, name) tuple.

        """
        return (raw_task[FIELD.ID], raw_task[FIELD.NAME])


    @staticmethod
    def _add_additional_fields(task, raw_task):
        """ Add the rest of the fields form the raw task to the Task.

        Required:
        Task task           The Task to finish constructing.
        dict raw_task       The raw task from the data source.

        Return:
        Task The Task built from the raw task.

        """
        task.set_description(raw_task[FIELD.DESCRIPTION])
        task.set_price(raw_task[FIELD.PRICE])


    @staticmethod
    def _convert_field_to_xml(field):
        """ Converts a field to xml by wrapping it in xml tags. """
        return "<blob>{}</blob>".format(field)


    @staticmethod
    def _retrieve_id(raw_task):
        """ Get the 'id' from the raw task. """
        asana_task = raw_task  # need to access asana fields.
        return asana_task[FIELD.ID]
