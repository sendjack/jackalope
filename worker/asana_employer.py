""" Module: asana_employer

AsanaEmployer subclasses Employer and handles all interaction between Jackalope
and Asana.

"""
# ran ./setup.py on pandemicsyn / asana
import xml.etree.cElementTree as ET
from asana import asana

import settings
from spec import Spec

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
        self._workspaces = AsanaEmployer.produce_dict(
                self._asana_api.list_workspaces())


    def read_specs(self):
        """ Return Specs from the Employer's service. """
        test_workspace_id = AsanaEmployer.retrieve_id(
                self._workspaces.get(settings.TEST_WORKSPACE_ID))

        tags = AsanaEmployer.produce_dict(
                self._asana_api.get_tags(test_workspace_id))

        test_tag_id = AsanaEmployer.retrieve_id(
                tags.get(settings.JACKALOPE_TAG_ID))

        short_asana_tasks = AsanaEmployer.produce_dict(
                self._asana_api.get_tag_tasks(test_tag_id))

        specs = {}
        for asana_task_id in short_asana_tasks.keys():
            spec = self._construct_spec(
                    self._asana_api.get_task(asana_task_id))
            specs[spec.id] = spec

        return specs


    def _construct_spec(self, raw_spec):
        """ Construct Spec from the raw spec.

        Required:
        dict raw_spec       The raw spec from the data source.

        Return:
        Spec         The Spec built from the raw spec.

        """
        asana_task = raw_spec  # accessing asana specific fields

        # get required  mapped fields
        service = FIELD_SERVICE
        id = asana_task[FIELD_ID]
        name = asana_task[FIELD_NAME]

        # get required embedded fields
        price = AsanaEmployer._extract_field(asana_task, FIELD_PRICE)

        # get optional mapped fields
        description = AsanaEmployer._extract_description(asana_task)

        # get optional embedded fields

        spec = Spec(id, service, name, price)
        spec.set_description(description)

        return spec


    @staticmethod
    def _extract_description(asana_task):
        """ Use the "notes" field but remove the embedded content. """
        xml_blob = AsanaEmployer._convert_field_to_xml(
                asana_task.get(FIELD_NOTES))
        return ET.XML(xml_blob).text.strip()


    @staticmethod
    def _extract_field(asana_task, field):
        """ Extract the embedded field in "notes" and return it. """
        xml_blob = AsanaEmployer._convert_field_to_xml(
                asana_task.get(FIELD_NOTES))
        elem = ET.XML(xml_blob)
        return elem.find(field).text.strip()


    @staticmethod
    def _convert_field_to_xml(field):
        """ Converts a field to xml by wrapping it in xml tags. """
        return "<blob>{}</blob>".format(field)


    @staticmethod
    def retrieve_id(asana_object):
        """ Get the ID from the asana_object. """
        return asana_object[FIELD_ID]


    @staticmethod
    def produce_dict(asana_list):
        """ Convert the list into a dict keyed on ID. """
        return {AsanaEmployer.retrieve_id(a): a for a in asana_list}