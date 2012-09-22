""" Module: spec

The Spec is a generic specification for a task.
Typically instructions will taken from the Foreman's Spec and pushed to the
Worker's Spec.

"""
from util.decorators import constant


class _Status(object):

    """ Spec Status Constants. """

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


class Spec(object):

    """ A specification for a task.

    Required:
    id _id              The id of the Spec, pulled from the source.
    str _status         The Status of the Spec
    str _service        The Service's type.
    str _name           The name of the Spec, pulled from the source.
    int _price          The price of the Spec in US Dollars.

    Optional:
    str _description    The description of the Spec.

    """


    def __init__(self, id, service, name, price):
        """ Construct Spec

        Required:
        id id       The id of the Spec.
        str service The type of external service that is associated.
        str name    The name field of the Spec.
        str price   The price that the Foreman will pay for the Spec.

        """
        self._id = id
        self._status = STATUS.NEW
        self._service = service
        self._name = name
        self._price = price

        self._description = None

        if self.is_spec_ready():
            self._status = STATUS.SPECIFICATION_COMPLETE
        else:
            self._status = STATUS.SPECIFICATION_INCOMPLETE


    @property
    def id(self):
        """ Return Spec's id. """
        return self._id


    @property
    def name(self):
        """ Return Spec's name. """
        return self._name


    @property
    def price(self):
        """ Return Spec's price. """
        return self._price


    @property
    def description(self):
        """ Return Spec's description. """
        return self._description


    def set_description(self, description):
        """ Set the description for the Spec. """
        self._description = description


    def is_spec_ready(self):
        """ Return True if all the required fields have values. """
        if self._service and self._id and self._name and self._price:
            return True
        else:
            return False
