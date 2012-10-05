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
    def EMAIL(self):
        return "email"

    @constant
    def DESCRIPTION(self):
        return "description"

    @constant
    def NOTES(self):
        return "notes"

    @constant
    def RECIPROCAL_ID(self):
        return "reciprocal_id"

    @constant
    def CATEGORY(self):
        return "tag"

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
        raw_task = self._asana_api.get_task(task_id)

        return self._construct_task(raw_task)


    def read_tasks(self):
        """ Connect to Worker's service and return all tasks.

        Return:
        dict    all the Tasks keyed on id

        """
        test_workspace_id = self._retrieve_id(
                self._workspaces.get(settings.TEST_WORKSPACE_ID))

        # FIXME: should be polling for tasks assigned to Jack, not tagged
        tags = self._produce_dict(
                self._asana_api.get_tags(test_workspace_id))

        test_tag_id = AsanaEmployer._retrieve_id(
                tags.get(settings.JACKALOPE_TAG_ID))

        short_asana_tasks = self._produce_dict(
                self._asana_api.get_tag_tasks(test_tag_id))

        tasks = {}
        for asana_task_id in short_asana_tasks.keys():
            raw_task = self._asana_api.get_task(asana_task_id)
            task = self._construct_task(raw_task)
            tasks[asana_task_id] = task

        return tasks


    def _embedded_fields(self):
        """ A list of embedded fields for this service. """
        return [
                FIELD.DESCRIPTION,
                FIELD.PRICE,
                FIELD.EMAIL,
                FIELD.RECIPROCAL_ID,
                FIELD.CATEGORY
                ]


    def _extract_field(self, asana_task, field=None):
        """ Extract the embedded field and return it. """
        notes = asana_task.get(self._embedding_field)
        elem = AsanaEmployer._convert_field_to_xml(notes)

        # when a field is specified, search the blob for a child
        if field is not None:
            elem = elem.find(field)

        text = ""
        if elem is not None:
            if elem.text is not None:
                text = elem.text

        return text.strip()


    def _embed_field(self, embedding_value, field, value):
        """ Embed the field, value in the embedding value. """
        return "{}\n{}".format(
                embedding_value,
                self._template_field(field, value))


    @staticmethod
    def _extract_required_fields(raw_task):
        """ Extract the required fields from the raw_task dict and return them.

        Required:
        dict raw_task       The raw task dictionary.

        Return:
        tuple (id, str) - return the the (id, name) tuple.

        """
        return (raw_task[FIELD.ID], raw_task[FIELD.NAME])


    @staticmethod
    def _extract_category(raw_task):
        """ Extract the category from the raw task and return it.

        Required:
        dict raw_task       The raw task dictionary.

        Return: str

        """
        return raw_task[FIELD.CATEGORY]


    def request_fields(self, task):
        # update descr with needed fields
        # comment back to employer with explanation
        # TODO: assign back to assigner

        # from the tag[s], get the [required] fields
        # FIXME: we can only use this hack because there is one field and we
        # won't get here unless that exact field is not present.
        fields = [FIELD.EMAIL]

        # FIXME: need to dedup templates+task.description
        # FIXME: need to append templates to task.description
        templates = [self._template_field(f) for f in fields]
        notes = "{}\n{}".format(task.description, "\n".join(templates))

        preface = "Please include the following fields in the Notes: "
        comment = "{}{}".format(preface, "; ".join(fields))

        return all([
                self._asana_api.update_task(task.id, notes=notes),
                self._add_comment(task.id, comment),
                ])


    def finish_task(self, task):
        # mark as complete
        # comment back to employer with a thank you note.
        # TODO: assign back to assigner
        return all([
                self._asana_api.update_task(
                    task.id,
                    assignee=None,
                    completed=True),
                self._add_comment(task.id, "All done!"),
                ])


    def _template_field(self, field, example=""):
        """ Return a templated field string, sometimes with an example. """
        #return "{}: {}".format(field, example)
        return "<{}>{}</{}>".format(field, example, field)


    def _add_comment(self, task_id, message):
        """ Add a comment to Provide an internal convenience wrapper. """
        return self._asana_api.add_story(task_id, message)


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
        task.set_email(raw_task[FIELD.EMAIL])


    @staticmethod
    def _convert_field_to_xml(field):
        """ Converts a field to xml by wrapping it in xml tags. """
        return ET.XML("<blob>{}</blob>".format(field))


    @staticmethod
    def _retrieve_id(raw_task):
        """ Get the 'id' from the raw task. """
        asana_task = raw_task  # need to access asana fields
        return asana_task[FIELD.ID]
