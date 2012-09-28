""" Module: task

Task is a specification for a task that can be used to pass data between
services. The Foreman will use Tasks to coordinate activity.

"""


class Task(object):

    """ A specification for a task.

    Required:
    id _id              The id of the Task, pulled from the source.
    str _service        The Service's type.
    str _name           The name of the Task, pulled from the source.
    int _price          The price of the Task in US Dollars.

    Optional:
    str _description    The description of the Task.

    """


    def __init__(self, id, service, name):
        """ Construct Task.

        Required:
        id id       The id of the Task.
        str service The type of external service that is associated.
        str name    The name field of the Task.

        """
        self._id = id
        self._service = service
        self._name = name

        self._description = None


    @property
    def id(self):
        """ Return id. """
        return self._id


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
    def description(self):
        """ Return description. """
        return self._description


    def set_description(self, description):
        """ Set the description. """
        self._description = description


    def is_spec_complete(self):
        """ Return True if all the required fields have values. """
        return all(self._get_required_fields())


    def _get_required_fields(self):
        """ Return a list of the required fields. """
        return [
                self._service,
                self._id,
                self._name,
                # FIXME: uncomment this!
                #self._price,
                # FIXME: remove this!
                self._email,
                ]


class RegistrationTask(Task):

    """ A Task for registering a new user with Jackalope.

    Required:
    str _tag    The type of task.

    """


    def __init__(self, id, service, name, description, tag):
        """ Construct RegistrationTask.

        Required:
        id id       The id of the Task.
        str service The type of external service that is associated.
        str name    The name field of the Task.
        str description The description of the Task.
        str tag         The typeof task.

        """
        super(RegistrationTask, self).__init__(id, service, name)
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
    def instantiate_task(class_, task_type, task_id, service, name):
        """ Use the task type to construct a Task.

        Required:
        str task_type       The specific type of Task.
        id  task_id         The service id of the Task.
        str service         The service that created the Task.
        str name            The name of the Task.

        Return: Task

        """
        task_init_function = class_.TASK_TYPE_MAPPING.get(task_type, Task)
        task = task_init_function(task_id, service, name)
        return task
