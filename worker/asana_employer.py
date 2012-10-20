""" Module: asana_employer

AsanaEmployer subclasses Employer and handles all interaction between Jackalope
and Asana.

"""
from asana import asana

from util.decorators import constant
import settings
from phrase import Phrase

from base import Employer, Transformer, FIELD, VALUE


class _AsanaField(object):

    """ These constants contain special fields for interacting with the Asana
    task. """

    @constant
    def NOTES(self):
        return "notes"

    @constant
    def TAG(self):
        return "tag"

    @constant
    def COMPLETED(self):
        return "completed"

ASANA_FIELD = _AsanaField()


class _Asana(object):

    """ These constants contain miscellaneous special Asana values. """

    @constant
    def ME(self):
        return "me"

ASANA = _Asana()


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

        short_asana_tasks = self._produce_dict(
                self._asana_api.list_tasks(test_workspace_id, ASANA.ME))

        tasks = {}
        for asana_task_id in short_asana_tasks.keys():
            raw_task = self._asana_api.get_task(asana_task_id)
            transformer = AsanaTransformer()
            transformer.set_raw_task(raw_task)
            tasks[asana_task_id] = self._ready_spec(transformer.get_task())

        return tasks


    def update_task(self, task):
        """ Connect to Worker's service and udpate the task.

        Required:
        Task task   The Task to update.

        Return:
        Task - updated Task.

        """
        print ""
        print "about to update:------"
        task._print_task()

        transformer = AsanaTransformer()
        transformer.set_task(task)

        new_raw_task_dict = self._asana_api.update_task(
                task.id(),  # task id
                task.name(),  # task name
                None,  # updated assignee
                None,  # assignee status
                transformer.is_asana_completed(),  # update completed status
                None,  # updated due date
                transformer.get_embedded_field_value())  # update notes

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

        # FIXME update all the fields instead of just status
        # task.set_email("")

        preface = "Please include the following fields in the Notes: "
        comment = "{}{}".format(preface, "; ".join(fields_to_request))

        return all([
                self.update_task(task),
                self.add_comment(task, comment),
                ])


    def update_task_to_created(self, task):
        """ Update the service's task's status to CREATED and return this
        updated Task.

        Required:
        Task task   The Task to update.

        Return:
        Task - updated Task.

        """
        print "here!"
        task.set_status_to_created()
        updated_task = self.update_task(task)
        # no add_comment with created

        return updated_task


    def update_task_to_posted(self, task):
        """ Update the service's task's status to POSTED and return this
        updated Task.

        Required:
        Task task   The Task to update.

        Return:
        Task - updated Task.

        """
        task.set_status_to_posted()
        updated_task = self.update_task(task)
        self.add_comment(task, Phrase.task_posted_note)

        return updated_task


    def update_task_to_assigned(self, task):
        """ Update the service's task's status to ASSIGNED and return this
        updated Task.

        Required:
        Task task   The Task to update.

        Return:
        Task - updated Task.

        """
        task.set_status_to_assigned()
        updated_task = self.update_task(task)
        self.add_comment(task, Phrase.task_assigned_note)

        return updated_task


    def update_task_to_completed(self, task):
        """ Update the service's task's status to COMPLETED and return this
        updated Task.

        Required:
        Task task   The Task to update.

        Return:
        Task - updated Task.

        """
        task.set_status_to_completed()
        updated_task = self.update_task(task)
        self.add_comment(task, Phrase.task_completed_note)

        return updated_task


    def update_task_to_approved(self, task):
        """ Update the service's task's status to APPROVED and return this
        updated Task.

        Required:
        Task task   The Task to update.

        Return:
        Task - updated Task.

        """
        # Asana shouldn't be getting approved notices but sending them.
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)


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


    def is_asana_completed(self):
        """ Return True if Asana's completed status is True. This corresponds
        to states VALUE.COMPLETED and VALUE.APPROVED. """
        is_completed = self.get_raw_task().get(ASANA_FIELD.COMPLETED)
        return is_completed


    def _pull_service_quirks(self, raw_task):
        """ Interact with the service in very service specific ways to pull
        additional fields into the raw task. """
        status_service_field = self._get_service_field_name(FIELD.STATUS)

        # if the completed field doesn't match the status then update it.
        is_asana_completed = raw_task.get(ASANA_FIELD.COMPLETED)
        status = raw_task.get(status_service_field)
        if (
                status == VALUE.CREATED or
                status == VALUE.POSTED or
                status == VALUE.ASSIGNED
                ):
            if is_asana_completed:
                raw_task[status_service_field] = VALUE.COMPLETED
        elif status == VALUE.COMPLETED or status == VALUE.APPROVED:
            if not is_asana_completed:
                print "this is an error in pull_service_quirks"
        return raw_task


    def _push_service_quirks(self, raw_task):
        """ Interact with the service in very service specific ways to push
        fields back into their proper spot. """
        status_service_field = self._get_service_field_name(FIELD.STATUS)

        # make sure that the completed field matches the status
        status = raw_task.get(status_service_field)
        if status == VALUE.COMPLETED or status == VALUE.APPROVED:
            raw_task[ASANA_FIELD.COMPLETED] = True
        else:
            raw_task[ASANA_FIELD.COMPLETED] = False

        return raw_task


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
                FIELD.LOCATION,
                FIELD.STATUS
                ]
