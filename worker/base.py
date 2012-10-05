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
        # flatten raw task dict
        raw_task = self._flatten_raw_task(raw_task)

        # build task
        (id, name) = self._extract_required_fields(raw_task)
        category = self._extract_category(raw_task)
        task = TaskFactory.instantiate_task(category, id, name)
        self._add_additional_fields(task, raw_task)

        # check to make sure spec is ready
        if not task.is_spec_ready():
            self.request_fields(task)
            task = None
            print "spec incomplete"

        return task


    def _deconstruct_task(self, task):
        """ Return raw task dict from Task. """
        # turn task into dict
        raw_task = self._pull_fields_from_task(task)

        # unflatten raw task dict
        raw_task = self._unflatten_raw_task(raw_task)

        return raw_task


    def _flatten_raw_task(self, raw_task):
        """ Pop embedding field, extract embedded fields, and update raw task
        dict. """
        # extract embedded
        embedded_fields_dict = {}
        for f in self._embedded_fields():
            embedded_fields_dict[f] = self._extract_field(raw_task, f)

        # remove embedding field and update
        raw_task.pop(self._embedding_field, None)
        raw_task.update(embedded_fields_dict)

        return raw_task


    def _unflatten_raw_task(self, raw_task):
        """ Insert embedded fields into embedding field, remove those fields
        from the dict, and add the new embedding field to the dict. """
        # pop embedded fields and insert them into embedding value
        embedding_value = ""
        for f in self._embedded_fields():
            value = raw_task.pop(f, None)
            embedding_value = self._embed_field(embedding_value, f, value)

        # add embedding field, remove embedded fields
        raw_task[self._embedding_field] = embedding_value

        return raw_task


    def _embedded_fields(self):
        """ A list of embedded fields for this service. """
        return []


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
        """ Extract the required fields from the raw_task dict and return them.

        Required:
        dict raw_task       The raw task dictionary.

        Return:
        tuple (id, str) - return the the (id, name) tuple.

        """
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)


    @staticmethod
    def _extract_category(raw_task):
        """ Extract the category from the raw task and return it.

        Required:
        dict raw_task       The raw task dictionary.

        Return: str

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


    def create_task(self, worker_task):
        """ Use a Worker's Task to create a task in the Worker's Service.

        Required:
        Task worker_task    the Worker's Task.

        Return:
        bool                True is successful

        """
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)
