""" Module: task

Task is a specification for a task that can be used to pass data between
services. The Foreman will use Tasks to coordinate activity.

All fields we handle should have accessors and mutators in the Task superclass.
The subclasses are used to define required fields and any special
functionality.

"""
from util.decorators import constant


class _Status(object):

    """ Task Status Constants. """

    @constant
    def POSTED(self):
        """ Task has been posted to/from Foreman/Worker. """
        return "posted"

    @constant
    def ASSIGNED(self):
        """ Task has been assigned to somebody to actually do. """
        return "assigned"

    @constant
    def COMPLETED(self):
        """ The outlined work in this Task is complete but under
        review. """
        return "completed"

    @constant
    def APPROVED(self):
        """ The work has been approved by the Employer and is closed
        out. """
        return "approved"

STATUS = _Status()


class Task(object):

    """ A specification for a task.

    Required:
    id _id              The id of the Task, pulled from the source.
    ServiceWorker _worker The ServiceWorker associated with this Task.
    str _status         The STATUS of the Task.
    str _name           The name of the Task, pulled from the source.

    Optional:
    id _reciprocal_id The Tasks's complimentary Task's id.
    str _description    The description of the Task.
    str _email          The email of attached to the Task.
    int _price          The price of the Task in US Dollars.

    """


    def __init__(self, id, name):
        """ Construct Task.

        Required:
        id id                       The id of the Task.
        str name                    The name field of the Task.

        """
        self._id = id
        self._status = STATUS.POSTED
        self._name = name

        self._reciprocal_id = None
        self._description = None
        self._email = None
        self._price = None



    @property
    def id(self):
        """ Return id. """
        return self._id


    def is_posted(self):
        """ Return True if the Task is POSTED. """
        return self._status == STATUS.POSTED


    def is_assigned(self):
        """ Return True if the Task is ASSIGNED. """
        return self._status == STATUS.ASSIGNED


    def is_completed(self):
        """ Return True if the Task is COMPLETED. """
        return self._status == STATUS.COMPLETED


    def is_approved(self):
        """ Return True if the Task is APPROVED. """
        return self._status == STATUS.APPROVED


    @property
    def name(self):
        """ Return name. """
        return self._name


    @property
    def price(self):
        """ Return price. """
        return self._price


    def set_price(self, price):
        """ Set the price. """
        self._price = price


    @property
    def email(self):
        """ Return email. """
        return self._email


    def set_email(self, email):
        """ Set the email. """
        self._email = email


    @property
    def reciprocal_id(self):
        """ Return reciprocal id. """
        return self._reciprocal_id


    def set_reciprocal_id(self, id):
        """ Set reciprocal id. """
        self._reciprocal_id = id


    @property
    def description(self):
        """ Return description. """
        return self._description


    def set_description(self, description):
        """ Set the description. """
        self._description = description


    def is_spec_ready(self):
        """ Return True if all the required fields have values. """
        return all(self._get_required_fields())


    def _get_required_fields(self):
        """ Return a list of the required fields. """
        return [
                self._status,
                self._id,
                self._name,
                ]


    def _print_task(self):
        """ Print all tasks. """
        print "\nTASK\n--------"
        print "id:", self.id
        print "name:", self.name
        print "price:", self.price
        print "email:", self.email
        print "description:", self.description
        print "spec ready?:", self.is_spec_ready()
        print ""


class RegistrationTask(Task):

    """ A Task for registering a new user with Jackalope.

    Required:
    str _email  The email field.

    """


    def _get_required_fields(self):
        """ Return a list of the required fields. """
        required_fields = super(RegistrationTask, self)._get_required_fields()
        required_fields.extend([
                self._email])
        return required_fields


class PricedTask(Task):

    """ A Task that forces the user to name a price.

    Required:
    str _price The price field.

    """


    def _get_required_fields(self):
        """ Return a list of the required fields. """
        required_fields = super(PricedTask, self)._get_required_fields()
        required_fields.extend([
                self._price])
        return required_fields


class TaskFactory(object):

    """ Use the type of task key to map to a specfic subclass of Task. """

    REGISTRATION = "registration"  # RegistrationTask
    PRICED = "priced"  # PricedTask


    # Used to map string task types with Task constructor functions.
    TASK_TYPE_MAPPING = {
            REGISTRATION: RegistrationTask,
            PRICED: PricedTask
            }


    @classmethod
    def instantiate_task(class_, task_type, task_id, name):
        """ Use the task type to construct a Task.

        Required:
        str task_type       The specific type of Task.
        id  task_id         The service id of the Task.
        str name            The name of the Task.

        Return: Task

        """
        task_constructor = class_.TASK_TYPE_MAPPING.get(task_type, Task)
        if type(task_constructor) == Task:
            print "oh yeah, we got one of them tasks"

        return task_constructor(task_id, name)
