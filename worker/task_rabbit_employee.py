""" Module: task_rabbit_employee

TaskRabbitEmployee subclasses Employee and handles all interaction between
Jackalope and TaskRabbit.

"""
import copy
import json
import requests

import settings
from task import Task

from base import Employee

FIELD_SERVICE = "task_rabbit"
FIELD_ID = "id"
FIELD_NAME = "name"
FIELD_PRICE = "named_price"
FIELD_DESCRIPTION = "description"
FIELD_CITY_ID = "city_id"
FIELD_ITEMS = "items"

CITY_ID = "4"

SITE = "https://taskrabbitdev.com"
AUTHORIZATION_HEADER = "Authorization"
OAUTH_PREFIX = "OAuth "
APPLICATION_HEADER = "X-Client-Application"
CONTENT_TYPE = "Content-Type"
APPLICATION_JSON = "application/json"

AUTHORIZE_URL = "https://taskrabbitdev.com/api/authorize"
TOKEN_URL = "https://taskrabbitdev.com/api/oauth/token"

TASKS_PATH = "/api/v1/tasks"


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
        return self._construct_task(raw_task)


    def read_tasks(self):
        """ Connect to Worker's service and return all tasks.

        Return:
        dict    all the Tasks keyed on id

        """
        items_dict = self._get(TASKS_PATH)
        task_rabbit_tasks = self._produce_dict(items_dict[FIELD_ITEMS])

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
        bool                True is successful

        """
        raw_task_dict = self._deconstruct_task(employee_task)
        return self._post(TASKS_PATH, raw_task_dict)


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


    def _construct_task(self, raw_task):
        """ Construct Task from the raw task.

        Required:
        dict raw_task   The raw task from the data source

        Return:
        Task            The Task built from the raw task.

        """
        tr_task = raw_task  # accessing task rabbit specific fields

        # get required mapped fields
        id = tr_task[FIELD_ID]
        name = tr_task[FIELD_NAME]

        # get optional mapped fields
        price = tr_task.get(FIELD_PRICE)
        description = tr_task.get(FIELD_DESCRIPTION)

        task = Task(id, self, name)
        task.set_price(price)
        task.set_description(description)

        return task


    def _deconstruct_task(self, employee_task):
        """ Deconstruct Task into a raw task.

        Required:
        Task employee_task  The Task to deconstruct into a dict

        Return:
        dict                The raw task to send to send to the Service

        """
        tr_task = {}

        # tr_task[FIELD_ID] = employee_task.id
        tr_task[FIELD_NAME] = employee_task.name
        tr_task[FIELD_PRICE] = int(employee_task.price)
        tr_task[FIELD_DESCRIPTION] = employee_task.description
        tr_task["city_id"] = 4

        tr_task_wrapper = {}
        tr_task_wrapper["task"] = tr_task
        return tr_task_wrapper


    @staticmethod
    def _retrieve_id(raw_task):
        """ Get the 'id' from the raw task. """
        task_rabbit_task = raw_task  # need to access task rabbit fields.
        return task_rabbit_task[FIELD_ID]
