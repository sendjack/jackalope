""" Module: task_rabbit_employee

TaskRabbitEmployee subclasses Employee and handles all interaction between
Jackalope and TaskRabbit.

"""
import copy
import json
import requests

from util.decorators import constant
import settings

from base import Employee


SITE = "https://taskrabbitdev.com"
AUTHORIZATION_HEADER = "Authorization"
OAUTH_PREFIX = "OAuth "
APPLICATION_HEADER = "X-Client-Application"
CONTENT_TYPE = "Content-Type"
APPLICATION_JSON = "application/json"

AUTHORIZE_URL = "https://taskrabbitdev.com/api/authorize"
TOKEN_URL = "https://taskrabbitdev.com/api/oauth/token"

TASKS_PATH = "/api/v1/tasks"


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
        return "named_price"

    @constant
    def DESCRIPTION(self):
        return "description"

    @constant
    def CITY_ID(self):
        return "city_id"

    @constant
    def ITEMS(self):
        return "items"

    @constant
    def TASK(self):
        return "task"

    @constant
    def RECIPROCAL_ID(self):
        return "reciprocal_id"

FIELD = _Field()


class TaskRabbitEmployee(Employee):

    """ Connect with TaskRabbit to allow requests.

    Required:
    dict _headers       headers to send with every type of request.

    """

    SERVICE = "task_rabbit"
    CITY_ID = "4"


    def __init__(self):
        """ Construct TaskRabbitEmployee. """
        self._embedding_field = None

        access_token = settings.TASK_RABBIT_ACCESS_TOKEN
        self._headers = {
                APPLICATION_HEADER: settings.TASK_RABBIT_SECRET,
                AUTHORIZATION_HEADER: OAUTH_PREFIX + access_token}


    def read_task(self, task_id):
        """ Connect to Worker's service and return the requested Task."""
        raw_task = self._get("{}/{}".format(TASKS_PATH, str(task_id)))

        return self._construct_task(raw_task)


    def read_tasks(self):
        """ Connect to Worker's service and return all tasks.

        Return:
        dict    all the Tasks keyed on id

        """
        items_dict = self._get(TASKS_PATH)
        task_rabbit_tasks = self._produce_dict(items_dict[FIELD.ITEMS])

        tasks = []
        for task_rabbit_task_id in task_rabbit_tasks.keys():
            task = self._construct_task(task_rabbit_tasks[task_rabbit_task_id])
            tasks[task.id] = task

        return tasks


    def create_task(self, employee_task):
        """ Use a Employee's Task to create a task in the Employee's Service.

        Required:
        Task employee_task      the Employee's Task.

        Return:
        Task the new Task.

        """
        raw_task_dict = self._deconstruct_task(employee_task)
        print raw_task_dict

        new_raw_task_dict = self._post(TASKS_PATH, raw_task_dict)
        return self._construct_task(new_raw_task_dict)


    def _get(self, path):
        """ Connect to TaskRabbit and issue a GET to the path.

        See: http://support.taskrabbit.com/entries/22024476

        Required:
        str     path to desired action

        Return:
        str         The parsed response.

        """
        url = SITE + path
        response = requests.get(url, headers=self._headers)

        return response.json


    def _post(self, path, data_dict):
        """ Connect to Employee's service with a POST request.

        Required:
        str path        path to desired action
        dict data_dict  data to post

        Return:
        str     The parsed response

        """
        url = SITE + path
        post_headers = copy.copy(self._headers)  # don't update reusable dict
        post_headers[CONTENT_TYPE] = APPLICATION_JSON

        response = requests.post(
                url,
                data=json.dumps(data_dict),
                headers=post_headers)

        return response.json


    def _deconstruct_task(self, employee_task):
        """ Deconstruct Task into a raw task.

        Required:
        Task employee_task  The Task to deconstruct into a dict

        Return:
        dict                The raw task to send to send to the Service

        """
        raw_task = super(TaskRabbitEmployee, self)._deconstruct_task(
                employee_task)
        task_wrapper = {}
        task_wrapper[FIELD.TASK] = raw_task

        return task_wrapper


    def _extract_from_embedding_field(self, tr_task):
        """ Remove the embedded content. """
        # Task Rabbit doesn't need an embedding field.
        return {}


    def _pull_fields_from_task(self, task):
        """ Grab fields from the Task and put them in the dict. """
        tr_task = {}

        # tr_task[FIELD_ID] = task.id
        tr_task[FIELD.NAME] = task.name
        tr_task[FIELD.PRICE] = int(task.price)
        tr_task[FIELD.DESCRIPTION] = task.description
        tr_task[FIELD.CITY_ID] = int(self.CITY_ID)

        return tr_task


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
        # optional
        # task.set_email(raw_task.get(FIELD.EMAIL))


    @staticmethod
    def _retrieve_id(raw_task):
        """ Get the 'id' from the raw task. """
        task_rabbit_task = raw_task  # need to access task rabbit fields.
        return task_rabbit_task[FIELD.ID]
