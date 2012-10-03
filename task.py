""" Module: task

Task is a specification for a task that can be used to pass data between
services. The Foreman will use Tasks to coordinate activity.

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
    int _price          The price of the Task in US Dollars.

    Optional:
    id _reciprocal_id The Tasks's complimentary Task's id.
    str _description    The description of the Task.

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


    @property
    def id(self):
        """ Return id. """
        return self._id


    @property
    def is_posted(self):
        """ Return True if the Task is POSTED. """
        return self._status == STATUS.POSTED


    @property
    def is_assigned(self):
        """ Return True if the Task is ASSIGNED. """
        return self._status == STATUS.ASSIGNED


    @property
    def is_completed(self):
        """ Return True if the Task is COMPLETED. """
        return self._status == STATUS.COMPLETED


    @property
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


    # FIXME: remove this!
    @property
    def email(self):
        """ Return email. """
        return self._email


    # FIXME: remove this!
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
                # FIXME: uncomment this!
                #self._price,
                # FIXME: remove this!
                #self._email,
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
    str _tag    The type of task.

    """


    def __init__(self, id, worker, name, description, tag):
        """ Construct RegistrationTask.

        Required:
        id id       The id of the Task.
        ServiceWorker _worker The ServiceWorker associated with this Task.
        str name    The name field of the Task.
        str description The description of the Task.
        str tag         The typeof task.

        """
        super(RegistrationTask, self).__init__(id, worker, name)
        self.set_description(description)
        self._tag = tag


    def _get_required_fields(self):
        """ Return a list of the required fields. """
        base_list = self._get_required_fields()
        base_list.extend([
                self._description,
                self._tag])
        return base_list


class TaskFactory(object):

    """ Use the type of task key to map to a specfic subclass of Task. """

    REGISTRATION = "registration"  # RegistrationTask

    # Used to map string task types with Task constructor functions.
    TASK_TYPE_MAPPING = {
            REGISTRATION: RegistrationTask
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
        task_init_function = class_.TASK_TYPE_MAPPING.get(task_type, Task)
        task = task_init_function(task_id, name)
        return task
