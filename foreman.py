""" Module: foreman

This module handles all coordination between Employer and Employee workers. 

TODO: Change all the names and make this work.
Each Task
has a ForemanSpec and a WorkerSpec. The TaskManager is in charge of resolving
differences between the Specs and making sure the Foreman or Worker handles the
needed resolution.

"""
from util.decorators import constant


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


class Task(object):

    """ Abstract superclass for structuring all Tasks.
    """


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
