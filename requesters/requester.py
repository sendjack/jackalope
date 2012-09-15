""" Module: requester

An outline of how a generic Requester should be structured.

"""
from util.decorators import constant
import settings


class _Status(object):

    """ Task Status Constants. """

    @constant
    def NEW(self):
        return "new"

    @constant
    def SPECIFICATION_INCOMPLETE(self):
        return "specification_incomplete"

    @constant
    def SPECIFICATION_COMPLETE(self):
        return "specification_complete"

    @constant
    def SUBMITTED(self):
        return "submitted"

    @constant
    def WORK_COMPLETE(self):
        return "work_complete"

    @constant
    def FINISHED(self):
        return "finished"

STATUS = _Status()


class Requester(object):

    """ Abstract superclass for connecting to external request apis. """


    def __init__(self):
        """ Construct Requester. """
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)


    def get_tasks(self):
        """ Return the Tasks that will be done. """
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)


class Task(object):

    """ Abstract superclass for structuring all Tasks.

    Required:
    str _status     The Status of the Task
    str _type       Requester type.
    id _id          The id of the task, pulled from the source.
    str _name       The name of the task, pulled from the source.
    int _price      The price of the task in US Dollars.

    """


    def __init__(self, proto_task):
        """ Construct Task.

        Required:
        dict proto_task     The raw task from the data source.

        """
        self._status = STATUS.NEW
        self._type = None
        self._id = None
        self._name = None
        self._price = None

        self._description = None

        self._construct_task(proto_task)

        if self.is_task_ready():
            self._status = STATUS.SPECIFICATION_COMPLETE
        else:
            self._status = STATUS.SPECIFICATION_INCOMPLETE

    @property
    def id(self):
        """ Return Task's id. """
        return self._id


    @property
    def name(self):
        """ Return Task's name. """
        return self._name


    @property
    def price(self):
        """ Return Task's price. """
        return self._price


    @property
    def description(self):
        """ Return Task's description. """
        return self._description


    def is_task_ready(self):
        """ Return True if all the required fields have values. """
        if self._type and self._id and self._name and self._price:
            return True
        else:
            return False


    def is_new(self):
        """ Return True if the Task's status is NEW. """
        if self._status == STATUS.NEW:
            return True
        else:
            return False


    def is_specification_incomplete(self):
        """ Return True if the Task's status is SPECIFICATION_INCOMPLETE. """
        if self._status == STATUS.SPECIFICATION_INCOMPLETE:
            return True
        else:
            return False


    def is_specification_complete(self):
        """ Return True if the Task's status is SPECIFICATION_COMPLETE. """
        if self._status == STATUS.SPECIFICATION_COMPLETE:
            return True
        else:
            return False


    def is_submitted(self):
        """ Return True if the Task's status is SUBMITTED. """
        if self._status == STATUS.SUBMITTED:
            return True
        else:
            return False


    def _construct_task(self, proto_task):
        """ Construct Task.

        Required:
        dict proto_task     The raw task from the data source.

        """
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)
