"""
    worker
    ------

    ServiceWorker is the base class for all interactions with external
    services' APIs, and provides an API for the Foreman/Workflow to interact
    with an external service.

    Employer (ServiceWorker) handles interactions with the Task
    requester (project management) services. Employee (ServiceWorker) handles
    interactions with the Task doer (outsourcing marketplace) service.

    ServiceWorker uses a TaskTransformer to handle mapping between the
    service's raw task dictionary and our raw task dictionary and our Tasks and
    a CommentTransformer to handle mapping between the service's raw comment
    dictionary and our raw Comment.

    Each service has its own ServiceWorker, TaskTransformer, and
    CommentTransformer subclasses.

"""
import copy
import json
import requests

from jutil.errors import OverrideRequiredError, OverrideNotAllowedError

from .client import REQUEST


class ServiceWorker(object):

    """Abstract superclass for connecting to external apis."""


    def __init__(self):
        raise OverrideRequiredError()


    def name(self):
        """Return the name of the vendor."""
        raise OverrideRequiredError()


    def create_task(self, task):
        """Use the Task to create a task in the Worker's service and then
        return the new Task."""
        raise OverrideRequiredError()


    def read_task(self, task_id):
        """Connect to the ServiceWorker's service and return a Task."""
        raise OverrideRequiredError()


    def read_tasks(self):
        """ Connect to Worker's service and return all tasks.

        Return:
        dict    all the Tasks keyed on id

        """
        raise OverrideRequiredError()


    def update_task(self, task):
        """Connect to worker's service and update the task."""
        raise OverrideRequiredError()


    def request_fields(self, task):
        """ Request from the service additional fields. """
        raise OverrideRequiredError()


    def add_comment(self, task_id, message):
        """Create a comment in the service on a task."""
        raise OverrideRequiredError()


    def read_comments(self, task_id):
        """Read Comments for a task from service and return a dict keyed on
        id."""
        raise OverrideRequiredError()


    def _get(self, protocol, domain, path):
        """ Connect to a service with a GET request."""
        url = unicode("{}://{}{}").format(
                protocol,
                domain,
                path)
        response = requests.get(url, headers=self._headers)

        return response.json


    def _post(self, protocol, domain, path, data_dict):
        """ Connect to a service with a POST request and return a dict."""
        url = unicode("{}://{}{}").format(
                protocol,
                domain,
                path)
        post_headers = copy.copy(self._headers)  # don't update reusable dict
        post_headers[REQUEST.CONTENT_TYPE] = REQUEST.APP_JSON

        response = requests.post(
                url,
                data=json.dumps(data_dict),
                headers=post_headers)

        return response.json


    def _put(self, protocol, domain, path, data_dict):
        url = unicode("{}://{}{}").format(
                protocol,
                domain,
                path)
        put_headers = copy.copy(self._headers)  # don't update reusable dict
        put_headers[REQUEST.CONTENT_TYPE] = REQUEST.APP_JSON

        response = requests.put(
                url,
                data=json.dumps(data_dict),
                headers=put_headers)

        return response.json


    def _ready_spec(self, task):
        """ Check to make sure task has a ready spec before handing it over to
        the Foreman. """
        if task.is_spec_ready():
            print "task", task.id(), "is ready"
            if not task.has_status():
                task.set_status_to_created()
                self.update_task(task)
        else:
            print "task", task.id(), "is not spec ready"
            if task.is_created():
                # TODO: some diff here to see if things have changed
                print "but has already been created."
            else:
                print "but has not been created. creating now..."
                task.set_status_to_created()
                self.request_required_fields(task)
            task = None

        return task


    # FIXME: produce_dict and retrieve_id are clearly part of Transformer.
    def _produce_dict(self, raw_tasks):
        """ Convert the list of raw tasks into a dict keyed on 'id'. """
        return {self._retrieve_id(t): t for t in raw_tasks}


    def _retrieve_id(self, raw_task):
        """ Get the 'id' from the raw_task. """
        # FIXME: This needs to got through the field map
        return raw_task[unicode("id")]


class Employer(ServiceWorker):

    """ Abstract superclass for interacting with Employer (e.g., project
    management services. """


    def __init__(self):
        raise OverrideRequiredError()


    def create_task(self, worker_task):
        """ Employers do not create tasks, their external services do. """
        raise OverrideNotAllowedError()


class Employee(ServiceWorker):

    """ Abstract superclass for interacting with Employee (e.g., task doers)
    services."""


    def __init__(self):
        raise OverrideRequiredError()
