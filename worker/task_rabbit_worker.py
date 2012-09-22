""" Module: task_rabbit_worker

TaskRabbitWorker subclasses Worker and handles all interaction between
Jackalope and TaskRabbit.

"""
# Use the py_oauth2 library
# https://github.com/liluo/py-oauth2
import oauth2
import json

import settings
from spec import Spec

from base import Worker

FIELD_SERVICE = "task_rabbit"
FIELD_ID = "id"
FIELD_NAME = "name"
FIELD_PRICE = "named_price"
FIELD_DESCRIPTION = "description"
FIELD_CITY_ID = "city_id"
FIELD_ITEMS = "items"

CITY_ID = "4"

SITE = "https://taskrabbitdev.com"
AUTHORIZE_URL = "https://taskrabbitdev.com/api/authorize"
TOKEN_URL = "https://taskrabbitdev.com/api/oauth/token"
HEADER_FORMAT = "OAuth %s"
APPLICATION_HEADER = "X-Client-Application"
CONTENT_TYPE = "Content-Type"
APPLICATION_JSON = "application_json"

TASKS_PATH = "/api/v1/tasks"


class TaskRabbitWorker(Worker):

    """ Connect with TaskRabbit to allow requests. """


    def __init__(self):
        """ Construct TaskRabbitWorker. """
        client = oauth2.Client(
                settings.TASK_RABBIT_KEY,
                settings.TASK_RABBIT_SECRET,
                site=SITE,
                authorize_url=AUTHORIZE_URL,
                token_url=TOKEN_URL,
                header_format=HEADER_FORMAT)

        self._access_token = client.auth_code.get_token(
                settings.TASK_RABBIT_USER_CODE,
                redirect_uri="")
        #self._access_token = oauth2.AccessToken(
                #client=client,
                #token=access_token,
                #header_format=HEADER_FORMAT)


    def read_spec(self, spec_id):
        """ Connect to Worker's service and return the requested spec.

        Return:
        Spec    the requested spec

        """
        raw_spec = self._get("{}/{}".format(TASKS_PATH, str(spec_id)))
        return self._construct_spec(raw_spec)


    def read_specs(self):
        """ Connect to Worker's service and return all specs.

        Return:
        dict    all the Specs keyed on id

        """
        task_rabbit_tasks = self._get(TASKS_PATH)
        raw_specs = task_rabbit_tasks[FIELD_ITEMS]
        # TODO make this dictionary happen in TaskManager
        raw_spec_dict = {s[FIELD_ID]: s for s in raw_specs}

        specs = []
        for task_rabbit_task_id in raw_spec_dict.keys():
            spec = self._construct_spec(raw_spec_dict[task_rabbit_task_id])
            specs[spec.id] = spec

        return specs


    def create_spec(self, worker_spec):
        """ Use a Worker's Spec to create a spec in the Worker's Service.

        Required:
        Spec worker_spec    the Worker's Spec.

        Return:
        bool                True is successful

        """
        spec_dict = self._deconstruct_spec(worker_spec)
        return self._post(TASKS_PATH, spec_dict)


    def _get(self, path):
        """ Connect to TaskRabbit and issue a GET to the path.

        See: http://support.taskrabbit.com/entries/22024476

        Required:
        str     path to desired action

        Return:
        str         The parsed response.

        """
        headers = {APPLICATION_HEADER: settings.TASK_RABBIT_SECRET}
        response = self._access_token.get(
                path,
                headers=headers)
        print "GET"
        print response
        print("body: {}".format(response.body))
        print("response: {}".format(response.response))
        print("reason: {}".format(response.reason))
        print("status: {}".format(response.status))
        print("ct: {}".format(response.content_type))
        print ""
        return response.parsed


    def _post(self, path, data_dict):
        """ Connect to Worker's service with a POST request.

        Required:
        str path        path to desired action
        dict data_dict  data to post

        Return:
        str     The parsed response

        """
        headers = {
                APPLICATION_HEADER: settings.TASK_RABBIT_SECRET,
                CONTENT_TYPE: APPLICATION_JSON}
        json_data = json.dumps(data_dict)
        print json_data
        response = self._access_token.post(
                path,
                body=json_data,
                headers=headers)

        print "POST"
        print response
        print("body: {}".format(response.body))
        print("response: {}".format(response.response))
        print("reason: {}".format(response.reason))
        print("status: {}".format(response.status))
        print("ct: {}".format(response.content_type))
        print ""
        return response.parsed


    def _construct_spec(self, raw_spec):
        """ Construct Spec from the raw spec.

        Required:
        dict raw_spec   The raw spec from the data source

        Return:
        Spec            The Spec built from the raw spec.

        """
        tr_task = raw_spec  # accessing task rabbit specific fields

        # get required mapped fields
        service = FIELD_SERVICE
        id = tr_task[FIELD_ID]
        name = tr_task[FIELD_NAME]

        # get optional mapped fields
        price = tr_task.get(FIELD_PRICE)
        description = tr_task.get(FIELD_DESCRIPTION)

        spec = Spec(id, service, name, price)
        spec.set_description(description)

        return spec


    def _deconstruct_spec(self, worker_spec):
        """ Deconstruct Spec into a raw spec.

        Required:
        Spec worker_spec    The Spec to deconstruct into a dict

        Return:
        dict                The raw spec to send to send to the Service

        """
        tr_task = {}

        # tr_task[FIELD_ID] = worker_spec.id
        tr_task[FIELD_NAME] = worker_spec.name
        tr_task[FIELD_PRICE] = worker_spec.price
        tr_task[FIELD_DESCRIPTION] = worker_spec.description

        tr_task_wrapper = {}
        tr_task_wrapper["task"] = tr_task
        return tr_task_wrapper
