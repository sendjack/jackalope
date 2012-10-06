""" Module: asana_employer

AsanaEmployer subclasses Employer and handles all interaction between Jackalope
and Asana.

"""
from asana import asana

from util.decorators import constant
import settings

from base import Employer, Transformer, FIELD


class _AsanaField(object):

    """ These constants contain special values for interacting with the Asana
    task. """

    @constant
    def NOTES(self):
        return "notes"

    @constant
    def TAG(self):
        return "tag"

ASANA_FIELD = _AsanaField()


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
        raw_task = self._asana_api.get_task(task_id)

        transformer = AsanaTransformer()
        transformer.set_raw_task(raw_task)
        return self._ready_spec(transformer.get_task())


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

        test_tag_id = self._retrieve_id(
                tags.get(settings.JACKALOPE_TAG_ID))

        short_asana_tasks = self._produce_dict(
                self._asana_api.get_tag_tasks(test_tag_id))

        tasks = {}
        for asana_task_id in short_asana_tasks.keys():
            raw_task = self._asana_api.get_task(asana_task_id)
            transformer = AsanaTransformer()
            transformer.set_raw_task(raw_task)
            tasks[asana_task_id] = self._ready_spec(transformer.get_task())

        return tasks


    def update_task(self, task):
        """ Connect to Worker's service and update the task.

        Required:
        Task task   The Task to update.

        """
        transformer = AsanaTransformer()
        transformer.set_task(task)

        new_raw_task_dict = self._asana_api.update_task(
                task.id(),
                task.name(),
                None,
                None,
                False,
                None,
                transformer.embedded_field_value)

        new_transformer = AsanaTransformer()
        new_transformer.set_raw_task(new_raw_task_dict)
        return self._ready_spec(new_transformer.get_task())


    def request_required_fields(self, task):
        """ Request unfilled but required fields. """
        # TODO: assign back to assigner
        accessors_to_request = []
        for accessor in task.get_required_accessors():
            if accessor() is None:
                accessors_to_request.append(accessor)

        transformer = AsanaTransformer()
        transformer.set_task(task)
        fields_to_request = transformer.transform_accessors_to_fields(
                task,
                accessors_to_request)

        # task.set_email("")

        preface = "Please include the following fields in the Notes: "
        comment = "{}{}".format(preface, "; ".join(fields_to_request))

        return all([
                # self.update_task(task),
                self.add_comment(task, comment),
                ])


    def update_task_to_completed(self, task):
        """ Set the Task's status as COMPLETED. """
        # TODO: assign back to assigner
        updated_raw_task = self._asana_api.update_task(
                task.id(),
                assignee=None,
                completed=True)
        self.add_comment(task, "All done!")

        transformer = AsanaTransformer()
        transformer.set_raw_task(updated_raw_task)
        return self._ready_spec(transformer.get_task())


    def add_comment(self, task, message):
        """ Add a comment to Provide an internal convenience wrapper. """
        return self._asana_api.add_story(task.id(), message)


class AsanaTransformer(Transformer):

    """ Handle parsing the service's response dictionary to construct a Task
    and deconstructing a Task into a raw task dictionary for the service.

    Required:
    str _embedding_field        The field to use to embed other fields.

    """


    def __init__(self):
        """ Construct an AsanaTransformer. """
        super(AsanaTransformer, self).__init__(ASANA_FIELD.NOTES)


    @property
    def embedded_field_value(self):
        """ Return the value representing a Task's embedded fields.

        Note: similar to deconstruct_task.

        """
        print "TODO: embedded field value"
        pass


    def _get_field_name_map(self):
        """ Return a mapping of our field names to Asana's field names. """
        field_name_map = super(AsanaTransformer, self)._get_field_name_map()
        field_name_map[FIELD.CATEGORY] = ASANA_FIELD.TAG

        return field_name_map


    def _embedded_fields(self):
        """ Return a list of embedded fields as Jackalope field names. """
        return [
                FIELD.DESCRIPTION,
                FIELD.PRICE,
                FIELD.EMAIL,
                FIELD.RECIPROCAL_ID,
                FIELD.CATEGORY,
                FIELD.LOCATION
                ]
