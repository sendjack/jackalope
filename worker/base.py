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


    def read_spec(self, spec_id):
        """ Connect to Worker service and return the requested spec.

        Return:
        Spec        the requested Spec

        """
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)


    def read_specs(self):
        """ Connect to Worker's service and return all specs.

        Return:
        dict    all the Specs keyed on id

        """
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)


    def create_spec(self, worker_spec):
        """ Use a Worker's Spec to create a spec in the Worker's Service.

        Required:
        Spec worker_spec    the Worker's Spec.

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


    def _construct_spec(self, raw_spec):
        """ Construct Spec from the raw spec.

        Required:
        dict raw_spec   The raw spec from the data source

        Return:
        Spec            The Spec built from the raw spec.

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
