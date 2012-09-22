""" Module: base

ServiceWorker is the base class for all interactions with external service's
APIs. Employer (ServiceWorker) handles interactions with task doer type
services and Employee (ServiceWorker) handles interactions with project
management type services. Each service/API will have its own subclass.

"""
import settings


class ServiceWorker(object):

    """ Abstract superclass for connecting to external apis. """


    def __init__(self):
        """ Construct ServiceWorker. """
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)


    def read_task(self, task_id):
        """ Connect to Worker's service and return the requested Task."""
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)


    def read_tasks(self):
        """ Connect to Worker's service and return all tasks.

        Return:
        dict    all the Tasks keyed on id

        """
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)


    def create_task(self, worker_task):
        """ Use a Worker's Task to create a task in the Worker's Service.

        Required:
        Task worker_task    the Worker's Task.

        Return:
        bool                True is successful

        """
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)


    def _get(self, path):
        """ Connect to Worker's service with a GET request.

        Required:
        str     path to desired action

        Return:
        str     The parsed response

        """
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)


    def _post(self, path, data):
        """ Connect to Worker's service with a POST request.

        Required:
        str     path to desired action
        str     data to post

        Return:
        str     The parsed response

        """
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)


    def _construct_task(self, raw_task):
        """ Construct Task from the raw task.

        Required:
        dict raw_task   The raw task from the data source

        Return:
        Task The Task built from the raw task.

        """
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)


class Employer(ServiceWorker):

    """ Abstract superclass for interacting with Employer (e.g., project
    management services. """


    def __init__(self):
        """ Construct Employer. """
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)


class Employee(ServiceWorker):

    """ Abstract superclass for interacting with Employee (e.g., task doers)
    services."""


    def __init__(self):
        """ Construct Employee. """
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)
