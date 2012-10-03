""" Module: base

ServiceWorker is the base class for all interactions with external service's
APIs. Employer (ServiceWorker) handles interactions with task doer type
services and Employee (ServiceWorker) handles interactions with project
management type services. Each service/API will have its own subclass.

"""
import settings
from task import TaskFactory


class ServiceWorker(object):

    """ Abstract superclass for connecting to external apis.

    Required:
    str _embedding_field        The field to use to embed other fields.

    """


    def __init__(self):
        """ Construct ServiceWorker. """
        self._embedding_field = None
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
        # extract embedded tasks
        embedding_field = self._embedding_field
        embedded_fields_dict = self._extract_from_embedding_field(raw_task)

        # flatten the raw_task
        raw_task.pop(embedding_field, None)
        raw_task.update(embedded_fields_dict)

        # build task
        (id, name) = self._extract_required_fields(raw_task)
        task = TaskFactory.instantiate_task(None, id, name)
        self._add_additional_fields(task, raw_task)

        # check to make sure spec is ready
        if not task.is_spec_ready():
            self.request_fields(task)
            task = None
            print "spec incomplete"

        return task


    def _extract_from_embedding_field(self, asana_task):
        """ Extract the embedded content.

        TODO: Are all subclasses going to need this method?

        """
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)


    def _produce_dict(self, raw_tasks):
        """ Convert the list of raw tasks into a dict keyed on 'id'. """
        return {self._retrieve_id(t): t for t in raw_tasks}


    @staticmethod
    def _extract_required_fields(raw_task):
        """ Remove the required fields from the raw_task dict and return them.

        Required:
        dict raw_task       The raw task dictionary.

        Return:
        tuple (id, str) - return the the (id, name) tuple.

        """
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)


    @staticmethod
    def _add_additional_fields(task, raw_task):
        """ Add the rest of the fields form the raw task to the Task.

        Required:
        Task task           The Task to finish constructing.
        dict raw_task       The raw task from the data source.

        Return:
        Task The Task built from the raw task.

        """
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)


    @staticmethod
    def _retrieve_id(raw_task):
        """ Get the 'id' from the raw_task. """
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
