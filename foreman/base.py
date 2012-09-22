""" Module: base

Foreman is the base class for all interactions with task creation APIs. These
external services act as 'foremen' for task creation and assignment. Each
service/API will have its own subclass.

"""
import settings


class Foreman(object):

    """ Abstract superclass for connecting to external foreman apis. """


    def __init__(self):
        """ Construct Foreman. """
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)


    def read_specs(self):
        """ Return Specs from the Foreman's service. """
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)


    def _construct_spec(self, raw_spec):
        """ Construct Spec from the raw spec.

        Required:
        dict raw_spec       The raw spec from the data source.

        Return:
        Spec         The Spec built from the raw spec.

        """
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)
