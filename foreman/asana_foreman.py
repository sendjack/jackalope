""" Module: asana_foreman

AsanaForeman subclasses Foreman and handles all interaction between Jackalope
and Asana.

"""
# ran ./setup.py on pandemicsyn / asana
import xml.etree.cElementTree as ET
from asana import asana

import settings
from spec.foreman import ForemanSpec

from base import Foreman

FIELD_TYPE = "asana"
FIELD_ID = "id"
FIELD_NAME = "name"
FIELD_PRICE = "price"
FIELD_NOTES = "notes"


class AsanaForeman(Foreman):

    """ Connect with Asana to allow requests.

    Required:
    AsanaAPI _asana_api     a connection to the asana api
    dict _workspaces        all the user's workspaces, keyed on id

    """


    def __init__(self):
        """ Construct AsanaForeman. """
        self._asana_api = asana.AsanaAPI(
                settings.ASANA_API_KEY,
                debug=True)
        self._workspaces = AsanaForeman.produce_dict(
                self._asana_api.list_workspaces())


    def get_specs(self):
        """ Return ForemanSpecs from the Foreman's service. """
        test_workspace_id = AsanaForeman.retrieve_id(
                self._workspaces.get(settings.TEST_WORKSPACE_ID))

        tags = AsanaForeman.produce_dict(
                self._asana_api.get_tags(test_workspace_id))

        test_tag_id = AsanaForeman.retrieve_id(
                tags.get(settings.JACKALOPE_TAG_ID))

        short_asana_tasks = AsanaForeman.produce_dict(
                self._asana_api.get_tag_tasks(test_tag_id))

        specs = []
        for asana_task_id in short_asana_tasks.keys():
            spec = self._construct_spec(
                    self._asana_api.get_task(asana_task_id))
            specs.append(spec)

        return {s.id: s for s in specs}


    def _construct_spec(self, raw_spec):
        """ Construct Spec from the raw spec.

        Required:
        dict raw_spec       The raw spec from the data source.

        Return:
        ForemanSpec         The Spec built from the raw spec.

        """
        asana_task = raw_spec  # accessing asana specific fields

        # get required  mapped fields
        type = FIELD_TYPE
        id = asana_task[FIELD_ID]
        name = asana_task[FIELD_NAME]

        # get required embedded fields
        price = AsanaForeman._extract_field(asana_task, FIELD_PRICE)

        # get optional mapped fields
        description = AsanaForeman._extract_description(asana_task)

        # get optional embedded fields

        spec = ForemanSpec(id, type, name, price)
        spec.set_description(description)

        return spec


    @staticmethod
    def _extract_description(asana_task):
        """ Use the "notes" field but remove the embedded content. """
        xml_blob = AsanaForeman._convert_field_to_xml(
                asana_task.get(FIELD_NOTES))
        return ET.XML(xml_blob).text.strip()


    @staticmethod
    def _extract_field(asana_task, field):
        """ Extract the embedded field in "notes" and return it. """
        xml_blob = AsanaForeman._convert_field_to_xml(
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
        return {AsanaForeman.retrieve_id(a): a for a in asana_list}
