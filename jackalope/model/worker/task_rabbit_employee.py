""" Module: task_rabbit_employee

TaskRabbitEmployee subclasses Employee and handles all interaction between
Jackalope and TaskRabbit.

"""
from jutil.decorators import constant
from jutil import environment
from redflag import redflag

from model.comment import Comment

from .client import REQUEST
from .worker import Employee
from .transformer import TaskTransformer, FIELD, VALUE


class _TaskRabbitField(object):

    """Constants for Task Rabbit dictionary fields."""

    @constant
    def PRICE(self):
        return "named_price"

    @constant
    def LOCATION(self):
        return "city_id"

    @constant
    def ITEMS(self):
        return "items"

    @constant
    def TASK(self):
        return "task"

    @constant
    def STATE(self):
        return "state"

    @constant
    def COMMENT(self):
        return "comment"

    @constant
    def CONTENT(self):
        return "content"

    @constant
    def VIRTUAL(self):
        return "virtual"

    @constant
    def PRIVATE_RUNNER(self):
        return "private_runner"

    @constant
    def RUNNER(self):
        return "runner"

    @constant
    def EMAIL(self):
        return "email"

TASK_RABBIT_FIELD = _TaskRabbitField()


class _TaskRabbitValue(object):

    """Constants for Task Rabbit dictionary values."""

    @constant
    def OPENED(self):
        return "opened"

    @constant
    def ASSIGNED(self):
        return "assigned"

    @constant
    def COMPLETED(self):
        return "completed"

    @constant
    def CLOSED(self):
        return "closed"

    @constant
    def EXPIRED(self):
        return "expired"

    @constant
    def CANCELED(self):
        return "canceled"

TASK_RABBIT_VALUE = _TaskRabbitValue()


class _TaskRabbit(object):

    """Constants for interacting with Task Rabbit service."""

    @constant
    def VENDOR(self):
        return "task_rabbit"

    @constant
    def VENDOR_IN_HTML(self):
        return "taskrabbit"

    @constant
    def PROTOCOL(self):
        return "https"

    @constant
    def DOMAIN(self):
        return environment.get_unicode(unicode("TASK_RABBIT_DOMAIN"))

    @constant
    def AUTHORIZE_URL(self):
        return self.DOMAIN + "/api/authorize"

    @constant
    def TOKEN_URL(self):
        return self.DOMAIN + "/api/oauth/token"

    @constant
    def TASKS_PATH(self):
        return "/api/v1/tasks"

    @constant
    def CLOSE_TASK_ACTION(self):
        return "/close"

    @constant
    def KEY(self):
        return environment.get_unicode(unicode("TASK_RABBIT_KEY"))

    @constant
    def SECRET(self):
        return environment.get_unicode(unicode("TASK_RABBIT_SECRET"))

    @constant
    def ACCESS_TOKEN(self):
        return environment.get_unicode(unicode("TASK_RABBIT_ACCESS_TOKEN"))

    @constant
    def REDIRECT_URI(self):
        return environment.get_unicode(unicode("TASK_RABBIT_REDIRECT_URI"))

TASK_RABBIT = _TaskRabbit()


class TaskRabbitEmployee(Employee):

    """ Connect with TaskRabbit to allow requests.

    Required:
    dict _headers       headers to send with every type of request.

    """


    def __init__(self):
        self._headers = {
                REQUEST.APP_HEADER: TASK_RABBIT.SECRET,
                REQUEST.AUTH_HEADER: REQUEST.OAUTH + TASK_RABBIT.ACCESS_TOKEN,
                }

    @property
    def name(self):
        """Return the name of the vendor."""
        return TASK_RABBIT.VENDOR


    def create_task(self, task):
        """Use Task to create a task in the Worker's service and then return
        the new Task."""
        transformer = TaskRabbitTaskTransformer()
        transformer.set_task(task)
        raw_task_dict = transformer.get_raw_task()

        # TODO: do this check in the base class
        raw_task_dict.get(TASK_RABBIT_FIELD.TASK).pop(FIELD.ID)

        new_raw_task_dict = self._post(
                TASK_RABBIT.PROTOCOL,
                TASK_RABBIT.DOMAIN,
                TASK_RABBIT.TASKS_PATH,
                raw_task_dict)

        # now update private description with TR's task id
        tr_id = new_raw_task_dict.get(FIELD.ID)
        path = unicode("{}/{}").format(TASK_RABBIT.TASKS_PATH, tr_id)
        blurb = TaskRabbitTaskTransformer.get_jackalope_blurb(
                TASK_RABBIT.VENDOR_IN_HTML,
                tr_id)
        private_description = unicode("{}\n{}").format(
                new_raw_task_dict.get(FIELD.PRIVATE_DESCRIPTION),
                blurb)

        updated_fields_dict = {FIELD.PRIVATE_DESCRIPTION: private_description}
        new_raw_task_dict = self._put(
                TASK_RABBIT.PROTOCOL,
                TASK_RABBIT.DOMAIN,
                path,
                updated_fields_dict)

        new_transformer = TaskRabbitTaskTransformer()
        new_transformer.set_raw_task(new_raw_task_dict)

        return self._ready_spec(new_transformer.get_task())


    def read_task(self, task_id):
        """Connect to the ServiceWorker's service and return a Task."""
        path = unicode("{}/{}").format(TASK_RABBIT.TASKS_PATH, str(task_id))
        raw_task = self._get(
                TASK_RABBIT.PROTOCOL,
                TASK_RABBIT.DOMAIN,
                path)

        transformer = TaskRabbitTaskTransformer()
        transformer.set_raw_task(raw_task)
        return self._ready_spec(transformer.get_task())


    def read_tasks(self):
        """ Connect to Worker's service and return all tasks.

        Return:
        dict    all the Tasks keyed on id

        """
        items_dict = self._get(
                TASK_RABBIT.PROTOCOL,
                TASK_RABBIT.DOMAIN,
                TASK_RABBIT.TASKS_PATH)
        task_rabbit_tasks = self._produce_dict(
                items_dict[TASK_RABBIT_FIELD.ITEMS])

        tasks = {}
        for task_rabbit_task_id in task_rabbit_tasks.keys():
            transformer = TaskRabbitTaskTransformer()
            transformer.set_raw_task(task_rabbit_tasks[task_rabbit_task_id])
            tasks[task_rabbit_task_id] = self._ready_spec(
                    transformer.get_task())

        return tasks


    def update_task(self, task):
        """Connect to worker's service and update the task."""
        # TODO: make update_task work for the general case.
        # Get the task status from Task Rabbit using the task_id
        task_path = unicode("{}/{}").format(
                TASK_RABBIT.TASKS_PATH,
                str(task.id()))
        raw_task = self._get(
                TASK_RABBIT.PROTOCOL,
                TASK_RABBIT.DOMAIN,
                task_path)

        transformer = TaskRabbitTaskTransformer()
        transformer.set_raw_task(raw_task)
        tr_task = transformer.get_task()

        updated_task = None
        if not tr_task.is_approved() and task.is_approved():
            updated_task = self._close_task(task)

        return updated_task


    def _close_task(self, task):
        """Close an approved Task Rabbit the way TR makes us and return updated
        Task."""
        id = task.id()
        close_path = unicode("{}/{}{}").format(
                TASK_RABBIT.TASKS_PATH,
                str(id),
                TASK_RABBIT.CLOSE_TASK_ACTION)

        closed_task_dict = self._post(
                TASK_RABBIT.PROTOCOL,
                TASK_RABBIT.DOMAIN,
                close_path,
                {})
        closed_transformer = TaskRabbitTaskTransformer()
        closed_transformer.set_raw_task(closed_task_dict)

        return self._ready_spec(closed_transformer.get_task())


    def add_comment(self, task_id, message):
        """Create a comment in the service on a task."""
        # Get the runner_email from Task Rabbit using the task_id
        task_path = unicode("{}/{}").format(
                TASK_RABBIT.TASKS_PATH,
                str(task_id))
        raw_task = self._get(
                TASK_RABBIT.PROTOCOL,
                TASK_RABBIT.DOMAIN,
                task_path)
        runner_email = raw_task.get(TASK_RABBIT_FIELD.RUNNER, {}).get(
                TASK_RABBIT_FIELD.EMAIL)

        # If successful, send the runner an email.
        if runner_email:
            redflag.send_comment_on_task(
                    TASK_RABBIT.VENDOR_IN_HTML,
                    task_id,
                    runner_email,
                    message)

        return True


    def read_comments(self, task_id):
        """Read Comments for a task from service and return a dict keyed on
        id."""
        # the easiest way to get comments from task rabbit is through the task.
        #path = "{}/{}".format(TASK_RABBIT.TASKS_PATH, str(task_id))
        #raw_task = self._get(path)
        #
        ## extract the raw task rabbit comments from the raw task dict.
        #raw_comments = (
        #        TaskRabbitCommentTransformer.pull_tr_comments_from_task_dict(
        #                raw_task)
        #        )
        #
        ## convert raw comments to Comments
        #comments = {}
        #for raw_comment in raw_comments:
        #    comment = (
        #            TaskRabbitCommentTransformer.convert_dict_to_comment(
        #                    raw_comment)
        #            )
        #    comments[comment.id()] = comment
        print "fake comment coming from task rabbit"
        comment = Comment(-1, -1, unicode("partnership is key."))
        comments = {comment.id(): comment}
        return comments


class TaskRabbitTaskTransformer(TaskTransformer):

    """ Handle parsing the service's response dictionary to construct a Task
    and deconstructing a Task into a raw task dictionary for the service.

    Required:
    str _embedding_field        The field to use to embed other fields.

    """

    CITY_ID = "9999"


    def __init__(self):
        super(TaskRabbitTaskTransformer, self).__init__(None)


    def _deconstruct_task_to_dict(self):
        """ Deconstruct Task into a raw task dict and return it. """
        raw_task = super(
                TaskRabbitTaskTransformer,
                self)._deconstruct_task_to_dict()

        # TODO: Remove this when incoming tasks have location
        location_service_field = self._get_service_field_name(FIELD.LOCATION)
        if not raw_task.get(location_service_field):
            print "No Location, so adding one myself."
            raw_task[location_service_field] = self.CITY_ID
            raw_task[TASK_RABBIT_FIELD.VIRTUAL] = True

        task_wrapper = {}
        task_wrapper[TASK_RABBIT_FIELD.TASK] = raw_task

        return task_wrapper


    def _pull_service_quirks(self, raw_task):
        """ Interact with the service in very service specific ways to pull
        additional fields into the raw task.

        Note: Task Rabbit doesn't have a created state.

        """
        status_service_field = self._get_service_field_name(FIELD.STATUS)

        # pull the status value and translate to raw task.
        status = raw_task.get(status_service_field)
        posted_cond = status == TASK_RABBIT_VALUE.OPENED
        assigned_cond = status == TASK_RABBIT_VALUE.ASSIGNED
        completed_cond = status == TASK_RABBIT_VALUE.COMPLETED
        approved_cond = status == TASK_RABBIT_VALUE.CLOSED
        expired_cond = status == TASK_RABBIT_VALUE.EXPIRED
        canceled_cond = status == TASK_RABBIT_VALUE.CANCELED

        if posted_cond:
            raw_task[status_service_field] = VALUE.POSTED
        elif assigned_cond:
            raw_task[status_service_field] = VALUE.ASSIGNED
        elif completed_cond:
            raw_task[status_service_field] = VALUE.COMPLETED
        elif approved_cond:
            raw_task[status_service_field] = VALUE.APPROVED
        elif expired_cond:
            raw_task[status_service_field] = VALUE.EXPIRED
        elif canceled_cond:
            raw_task[status_service_field] = VALUE.CANCELED
        else:
            print "ERROR in pull service quirks"
            raw_task[status_service_field] = VALUE.POSTED

        return raw_task


    def _push_service_quirks(self, raw_task):
        """ Interact with the service in very service specific ways to push
        fields back into their proper spot.

        Note: Task Rabbit doesn't have a created state.

        """
        status_service_field = self._get_service_field_name(FIELD.STATUS)

        # convert our status value's to task rabbit's
        status = raw_task.get(status_service_field)
        created_cond = status == VALUE.CREATED
        posted_cond = status == VALUE.POSTED
        assigned_cond = status == VALUE.ASSIGNED
        completed_cond = status == VALUE.COMPLETED
        approved_cond = status == VALUE.APPROVED
        expired_cond = status == VALUE.EXPIRED
        canceled_cond = status == VALUE.CANCELED

        if posted_cond:
            raw_task[status_service_field] = TASK_RABBIT_VALUE.OPENED
        elif assigned_cond:
            raw_task[status_service_field] = TASK_RABBIT_VALUE.ASSIGNED
        elif completed_cond:
            raw_task[status_service_field] = TASK_RABBIT_VALUE.COMPLETED
        elif approved_cond:
            raw_task[status_service_field] = TASK_RABBIT_VALUE.CLOSED
        elif expired_cond:
            raw_task[status_service_field] = TASK_RABBIT_VALUE.EXPIRED
        elif canceled_cond:
            raw_task[status_service_field] = TASK_RABBIT_VALUE.CANCELED
        elif created_cond:
            print "there shouldn't be a created status state but there is."
        else:
            print "status push error"
            raw_task[status_service_field] = TASK_RABBIT_VALUE.OPENED

        # all task rabbit tasks should be private
        raw_task[TASK_RABBIT_FIELD.PRIVATE_RUNNER] = True

        return raw_task


    def _get_field_name_map(self):
        """ Return a mapping of our field names to Asana's field names. """
        field_name_map = super(
                TaskRabbitTaskTransformer,
                self)._get_field_name_map()
        field_name_map[FIELD.PRICE] = TASK_RABBIT_FIELD.PRICE
        field_name_map[FIELD.LOCATION] = TASK_RABBIT_FIELD.LOCATION
        field_name_map[FIELD.STATUS] = TASK_RABBIT_FIELD.STATE

        return field_name_map


    def _embedded_fields(self):
        """ Return a list of embedded fields as Jackalope field names. """
        return []
