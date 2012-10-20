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
    def CREATED(self):
        """ Task has been created but not yet posted. """
        return "created"

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
    str _category       The category of task.
    id _id              The id of the Task, pulled from the source.
    ServiceWorker _worker The ServiceWorker associated with this Task.
    str _status         The STATUS of the Task.
    str _name           The name of the Task, pulled from the source.

    Optional:
    id _reciprocal_id The Tasks's complimentary Task's id.
    str _description    The description of the Task.
    str _email          The email of attached to the Task.
    int _price          The price of the Task in US Dollars.
    int _location       The location of the Task by id.

    """


    def __init__(self, category, id, name):
        """ Construct Task.

        Required:
        str category                The category of Task.
        id id                       The id of the Task.
        str name                    The name field of the Task.

        """
        self._category = category
        self._id = id
        self._status = None  # doesn't get created until it's in the DB
        self._name = name

        self._reciprocal_id = None
        self._description = None
        self._email = None
        self._price = None
        self._location = None


    def category(self):
        """ Return task category. """
        return self._category


    def id(self):
        """ Return id. """
        return self._id


    def has_status(self):
        """ Return True if status isn't None. """
        return self._status is not None


    def is_created(self):
        """ Return True if the Task is CREATED. """
        return self._status == STATUS.CREATED


    def set_status_to_created(self):
        """ Set Status to CREATED. """
        self._status = STATUS.CREATED


    def is_posted(self):
        """ Return True if the Task is POSTED. """
        return self._status == STATUS.POSTED


    def set_status_to_posted(self):
        """ Set Status to POSTED. """
        self._status = STATUS.POSTED


    def is_assigned(self):
        """ Return True if the Task is ASSIGNED. """
        return self._status == STATUS.ASSIGNED


    def set_status_to_assigned(self):
        """ Set Status to ASSIGNED. """
        self._status = STATUS.ASSIGNED


    def is_completed(self):
        """ Return True if the Task is COMPLETED. """
        return self._status == STATUS.COMPLETED


    def set_status_to_completed(self):
        """ Set Status to COMPLETED. """
        self._status = STATUS.COMPLETED


    def is_approved(self):
        """ Return True if the Task is APPROVED. """
        return self._status == STATUS.APPROVED


    def set_status_to_approved(self):
        """ Set Status to APPROVED. """
        self._status = STATUS.APPROVED


    def name(self):
        """ Return name. """
        return self._name


    def price(self):
        """ Return price. """
        return self._price


    def set_price(self, price):
        """ Set the price. """
        if price:
            self._price = int(price)


    def email(self):
        """ Return email. """
        return self._email


    def set_email(self, email):
        """ Set the email. """
        self._email = email


    def reciprocal_id(self):
        """ Return reciprocal id. """
        return self._reciprocal_id


    def set_reciprocal_id(self, id):
        """ Set reciprocal id. """
        self._reciprocal_id = id


    def description(self):
        """ Return description. """
        return self._description


    def set_description(self, description):
        """ Set the description. """
        self._description = description


    def location(self):
        """ Return the location. """
        return self._location


    def set_location(self, location_id):
        """ Set the location. """
        if location_id:
            self._location = int(location_id)


    def is_spec_ready(self):
        """ Return True if all the required fields have values. """
        required_fields = [a() for a in self.get_required_accessors()]
        return all(required_fields)


    def get_required_accessors(self):
        """ Return a list of the required fields. """
        return [
                self.id,
                self.name,
                ]


    def _print_task(self):
        """ Print all tasks. """
        print "\nTASK\n--------"
        print "id:", self._id
        print "name:", self._name
        print "price:", self._price
        print "email:", self._email
        print "reciprocal_id", self._reciprocal_id
        print "status:", self._status
        print "description:", self.description()
        print "spec ready?:", self.is_spec_ready()
        print ""


class RegistrationTask(Task):

    """ A Task for registering a new user with Jackalope.

    Required:
    str _email  The email field.

    """


    def get_required_accessors(self):
        """ Return a list of the required fields. """
        required_accessors = super(
                RegistrationTask,
                self).get_required_accessors()
        required_accessors.extend([
                self.email])
        return required_accessors


class PricedTask(Task):

    """ A Task that forces the user to name a price.

    Required:
    str _price The price field.

    """


    def get_required_accessors(self):
        """ Return a list of the required fields. """
        required_accessors = super(PricedTask, self).get_required_accessors()
        required_accessors.extend([
                self.price])
        return required_accessors


class TaskFactory(object):

    """ Use the category of task key to map to a specfic subclass of Task. """

    REGISTRATION = "registration"  # RegistrationTask
    PRICED = "priced"  # PricedTask


    # Used to map string task categories with Task constructor functions.
    TASK_CATEGORY_MAPPING = {
            REGISTRATION: RegistrationTask,
            PRICED: PricedTask
            }


    @classmethod
    def instantiate_task(class_, category, task_id, name):
        """ Use the task category to construct a Task.

        Required:
        str category        The specific category of Task.
        id  task_id         The service id of the Task.
        str name            The name of the Task.

        Return: Task

        """
        task_constructor = class_.TASK_CATEGORY_MAPPING.get(category, Task)
        if type(task_constructor) == Task:
            print "oh yeah, we got one of them tasks"

        return task_constructor(category, task_id, name)
