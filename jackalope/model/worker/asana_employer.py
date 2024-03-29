"""
    asana_employer
    --------------

    Handle all interactions with Asana server and data transformations.

"""
import time
import dateutil.parser
import dateutil.tz
from asana import asana

from jutil.decorators import constant
from jutil import environment
from jutil.base_type import to_integer
#from jackalope.phrase import Phrase

from worker import Employer
from transformer import TaskTransformer, CommentTransformer, FIELD, VALUE


class _AsanaField(object):

    """Constants for Asana dictionary fields."""

    @constant
    def NOTES(self):
        return "notes"

    @constant
    def TAG(self):
        return "tag"

    @constant
    def COMPLETED(self):
        return "completed"

    @constant
    def CREATED_AT(self):
        return "created_at"

    @constant
    def CREATED_BY(self):
        return "created_by"

    @constant
    def TEXT(self):
        return "text"

    @constant
    def TYPE(self):
        return "type"

    @constant
    def PROJECTS(self):
        return "projects"

ASANA_FIELD = _AsanaField()


class _AsanaValue():

    """Constants for Asana dictionary values."""

    @constant
    def COMMENT(self):
        return "comment"

ASANA_VALUE = _AsanaValue()


class _Asana(object):

    """Constants for interacting with Asana service."""

    @constant
    def ME(self):
        return "me"

    @constant
    def API_KEY(self):
        return environment.get_unicode(unicode("ASANA_API_KEY"))

    @constant
    def JACK_USER_ID(self):
        return environment.get_integer(unicode("ASANA_USER_ID"))

    @constant
    def WORKSPACE_ID(self):
        return environment.get_integer(unicode("ASANA_WORKSPACE_ID"))

    @constant
    def DEV_PROJECT_ID(self):
        return environment.get_integer(unicode("ASANA_DEV_PROJECT_ID"))

    @constant
    def VENDOR(self):
        return "asana"

    @constant
    def VENDOR_IN_HTML(self):
        return "asana"

ASANA = _Asana()


class AsanaEmployer(Employer):

    """Connect with Asana to allow requests.

    Attributes
    ----------
    _asana_api : AsanaAPI
    _workspaces : dict

    """

    def __init__(self):
        self._asana_api = asana.AsanaAPI(
                ASANA.API_KEY,
                debug=False)
        self._workspaces = self._produce_dict(
                self._asana_api.list_workspaces())


    @property
    def name(self):
        """Return the name of the vendor."""
        return ASANA.VENDOR


    def read_task(self, task_id):
        """Return a Task from the vendor."""
        raw_task = self._asana_api.get_task(task_id)

        transformer = AsanaTaskTransformer()
        transformer.set_raw_task(raw_task)
        return self._ready_spec(transformer.get_task())


    def read_tasks(self):
        """Read all tasks from vendor and return Tasks as dict."""
        print "\nSTEP 1: READ ALL ASANA TASKS ------>\n"

        test_workspace_id = self._retrieve_id(
                self._workspaces.get(ASANA.WORKSPACE_ID))

        short_asana_tasks = self._produce_dict(
                self._asana_api.list_tasks(test_workspace_id, ASANA.ME))

        tasks = {}
        for asana_task_id in short_asana_tasks.keys():
            process_task = True
            raw_task = self._asana_api.get_task(asana_task_id)

            # only process tasks in the project
            if ASANA.DEV_PROJECT_ID:
                process_task = AsanaTaskTransformer.is_task_in_project(
                        raw_task,
                        ASANA.DEV_PROJECT_ID)

            if process_task:
                transformer = AsanaTaskTransformer()
                transformer.set_raw_task(raw_task)
                tasks[asana_task_id] = self._ready_spec(transformer.get_task())

        print "-------> ASANA TASKS READ. Return:", [k for k in tasks.keys()]

        return tasks


    def update_task(self, task):
        """Connect to Worker's service and update the task."""
        transformer = AsanaTaskTransformer()
        transformer.set_task(task)

        new_raw_task_dict = self._asana_api.update_task(
                task.id(),
                task.name(),
                None,  # updated assignee
                None,  # assignee status
                transformer.is_asana_completed(),
                None,  # updated due date
                transformer.get_embedding_field_value())  # update notes

        new_transformer = AsanaTaskTransformer()
        new_transformer.set_raw_task(new_raw_task_dict)

        # FIXME XXX: These need to be queued somewhere
        #self.add_comment(task.id(), Phrase.task_posted_note)
        #self.add_comment(task.id(), Phrase.task_assigned_note)
        #self.add_comment(task.id(), Phrase.task_completed_note)

        return self._ready_spec(new_transformer.get_task())


    def request_required_fields(self, task):
        """ Request unfilled but required fields. """
        # TODO: assign back to assigner
        accessors_to_request = []
        for accessor in task.get_required_accessors():
            if accessor() is None:
                accessors_to_request.append(accessor)

        transformer = AsanaTaskTransformer()
        transformer.set_task(task)
        fields_to_request = transformer.transform_accessors_to_fields(
                task,
                accessors_to_request)

        # FIXME update all the fields instead of just status
        # task.set_email("")

        preface = unicode("Please include the following fields in the Notes: ")
        comment = unicode("{}{}").format(preface, "; ".join(fields_to_request))

        return all([
                self.update_task(task),
                self.add_comment(task.id(), comment),
                ])


    def add_comment(self, task_id, message):
        """Create a comment in the service on a task."""
        return self._asana_api.add_story(to_integer(task_id), message)


    def read_comments(self, task_id):
        """Read Comments for a task from service and return a dict keyed on
        id.

        Note: Currently we're only returning the comments made by the service's
        user. Later this should be moved to a function in the Task.

        """
        raw_stories = self._read_stories(task_id)

        # pull raw comments from raw stories list.
        raw_comments = []
        for raw_story in raw_stories:
            is_story = AsanaCommentTransformer.is_story_a_comment(raw_story)
            is_user_post = AsanaCommentTransformer.is_user_post(raw_story)
            if is_story and is_user_post:
                raw_comments.append(raw_story)

        # convert raw comments to Comments
        comments = {}
        for raw_comment in raw_comments:
            comment = AsanaCommentTransformer.convert_dict_to_comment(
                    raw_comment)
            comments[comment.id()] = comment

        return comments


    def _read_stories(self, task_id):
        """Read Asana raw stories for a task and return them as a list."""
        return self._asana_api.list_stories(to_integer(task_id))


class AsanaTaskTransformer(TaskTransformer):

    """ Handle parsing the service's response dictionary to construct a Task
    and deconstructing a Task into a raw task dictionary for the service.

    Required:
    str _embedding_field        The field to use to embed other fields.

    """


    def __init__(self):
        super(AsanaTaskTransformer, self).__init__(ASANA_FIELD.NOTES)


    @classmethod
    def is_task_in_project(class_, raw_task, project_id):
        """Check to see if the project id is associated with the raw task."""
        is_task_in_project = False
        raw_projects_list = raw_task.get(ASANA_FIELD.PROJECTS)
        for p in raw_projects_list:
            if p.get(FIELD.ID) == project_id:
                is_task_in_project = True

        return is_task_in_project


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
        field_name_map = super(
                AsanaTaskTransformer,
                self)._get_field_name_map()
        field_name_map[FIELD.CATEGORY] = ASANA_FIELD.TAG

        return field_name_map


    def _embedded_fields(self):
        """ Return a list of embedded fields as Jackalope field names. """
        return [
                FIELD.DESCRIPTION,
                FIELD.PRICE,
                #FIELD.EMAIL,
                #FIELD.CATEGORY,
                #FIELD.LOCATION,
                FIELD.STATUS,
                ]


class AsanaCommentTransformer(CommentTransformer):

    """Transform an Asana comment dictionary into a Comment and the inverse."""


    @classmethod
    def convert_dict_to_comment(class_, raw_comment):
        """Convert a raw comment dict to a Comment and return it."""
        # convert the asana raw comment to a jackalope raw comment
        id = raw_comment[FIELD.ID]
        created_ts = class_._convert_datestring_to_epochseconds(
                raw_comment[ASANA_FIELD.CREATED_AT])
        message = raw_comment[ASANA_FIELD.TEXT]

        jack_raw_comment = {
                FIELD.ID: id,
                FIELD.CREATED_TS: created_ts,
                FIELD.MESSAGE: message
                }

        # hand the jackalope raw comment to super and return a Comment
        return super(AsanaCommentTransformer, class_).convert_dict_to_comment(
                jack_raw_comment)


    @classmethod
    def convert_comment_to_dict(class_, comment):
        """Convert a Comment to a raw comment dict and return it."""
        # TODO isn't used
        # hand the Comment to super and get a jackalope raw comment
        jack_raw_comment = super(
                AsanaCommentTransformer,
                class_).convert_comment_to_dict(comment)

        # convert the jackalope raw comment to an asana raw comment
        raw_comment = {}
        raw_comment[FIELD.ID] = jack_raw_comment[FIELD.ID]
        raw_comment[ASANA_FIELD.CREATED_AT] = jack_raw_comment[
                FIELD.CREATED_TS]
        raw_comment[ASANA_FIELD.TEXT] = jack_raw_comment[FIELD.MESSAGE]

        return raw_comment


    @classmethod
    def is_story_a_comment(class_, raw_story):
        """Asana has two types of stories, "system" and "comment"."""
        is_comment = False
        if raw_story[ASANA_FIELD.TYPE] == ASANA_VALUE.COMMENT:
            is_comment = True

        return is_comment

    @classmethod
    def is_user_post(class_, raw_story):
        """Return True if the story was posted by someone other than Jack."""
        creator_id = raw_story[ASANA_FIELD.CREATED_BY][FIELD.ID]

        return creator_id != ASANA.JACK_USER_ID


    @classmethod
    def _convert_datestring_to_epochseconds(class_, datestring):
        asana_dt = dateutil.parser.parse(datestring)
        # convert to local because timetuple is tz unaware and mktime is local
        local_dt = asana_dt.astimezone(dateutil.tz.tzlocal())

        return int(time.mktime(local_dt.timetuple()))
