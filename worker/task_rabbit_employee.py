""" Module: task_rabbit_employee

TaskRabbitEmployee subclasses Employee and handles all interaction between
Jackalope and TaskRabbit.

"""
import copy
import json
import requests

from util.decorators import constant
import settings

from base import Employee, Transformer, FIELD


SITE = "https://taskrabbitdev.com"
AUTHORIZATION_HEADER = "Authorization"
OAUTH_PREFIX = "OAuth "
APPLICATION_HEADER = "X-Client-Application"
CONTENT_TYPE = "Content-Type"
APPLICATION_JSON = "application/json"

AUTHORIZE_URL = "https://taskrabbitdev.com/api/authorize"
TOKEN_URL = "https://taskrabbitdev.com/api/oauth/token"

TASKS_PATH = "/api/v1/tasks"


class _TaskRabbitField(object):

    """ These constants contain special values for interacting with the
    Task Rabbit tasks. """

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

TASK_RABBIT_FIELD = _TaskRabbitField()


class TaskRabbitEmployee(Employee):

    """ Connect with TaskRabbit to allow requests.

    Required:
    dict _headers       headers to send with every type of request.

    """


    def __init__(self):
        """ Construct TaskRabbitEmployee. """
        access_token = settings.TASK_RABBIT_ACCESS_TOKEN
        self._headers = {
                APPLICATION_HEADER: settings.TASK_RABBIT_SECRET,
                AUTHORIZATION_HEADER: OAUTH_PREFIX + access_token}


    def read_task(self, task_id):
        """ Connect to Worker's service and return the requested Task."""
        raw_task = self._get("{}/{}".format(TASKS_PATH, str(task_id)))

        transformer = TaskRabbitTransformer()
        transformer.set_raw_task(raw_task)
        return self._ready_spec(transformer.get_task())


    def read_tasks(self):
        """ Connect to Worker's service and return all tasks.

        Return:
        dict    all the Tasks keyed on id

        """
        items_dict = self._get(TASKS_PATH)
        task_rabbit_tasks = self._produce_dict(
                items_dict[TASK_RABBIT_FIELD.ITEMS])

        tasks = {}
        for task_rabbit_task_id in task_rabbit_tasks.keys():
            transformer = TaskRabbitTransformer()
            transformer.set_raw_task(task_rabbit_tasks[task_rabbit_task_id])
            tasks[task_rabbit_task_id] = self._ready_spec(
                    transformer.get_task())

        return tasks


    def create_task(self, task):
        """ Use a Employee's Task to create a task in the Employee's Service.

        Required:
        Task task      the Employee's Task.

        Return:
        Task the new Task.

        """
        transformer = TaskRabbitTransformer()
        transformer.set_task(task)
        raw_task_dict = transformer.get_raw_task()

        # TODO: do this check in the base class
        raw_task_dict.get('task').pop("id")

        new_raw_task_dict = self._post(TASKS_PATH, raw_task_dict)
        new_transformer = TaskRabbitTransformer()
        new_transformer.set_raw_task(new_raw_task_dict)
        return self._ready_spec(new_transformer.get_task())


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


class TaskRabbitTransformer(Transformer):

    """ Handle parsing the service's response dictionary to construct a Task
    and deconstructing a Task into a raw task dictionary for the service.

    Required:
    str _embedding_field        The field to use to embed other fields.

    """

    CITY_ID = "4"


    def __init__(self):
        """ Construct a TaskRabbitTransformer. """
        super(TaskRabbitTransformer, self).__init__(None)


    def _deconstruct_task_to_dict(self):
        """ Deconstruct Task into a raw task dict and return it. """
        raw_task = super(
                TaskRabbitTransformer,
                self)._deconstruct_task_to_dict()

        # TODO: Remove this
        location_service_field = self._get_service_field_name(FIELD.LOCATION)
        if not raw_task.get(location_service_field):
            print "No Location, so adding one myself."
            raw_task[location_service_field] = self.CITY_ID

        task_wrapper = {}
        task_wrapper[TASK_RABBIT_FIELD.TASK] = raw_task

        return task_wrapper


    def _get_field_name_map(self):
        """ Return a mapping of our field names to Asana's field names. """
        field_name_map = super(
                TaskRabbitTransformer,
                self)._get_field_name_map()
        field_name_map[FIELD.PRICE] = TASK_RABBIT_FIELD.PRICE
        field_name_map[FIELD.LOCATION] = TASK_RABBIT_FIELD.LOCATION

        return field_name_map


    def _embedded_fields(self):
        """ Return a list of embedded fields as Jackalope field names. """
        return []
