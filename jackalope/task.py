"""
    task
    ----

    Task is a specification for a service's task that can be used to compare
    between service and communicate with our central processing unit, Foreman.

    Notes
    +++++
    All service fields have corresponding accessors and mutators in the Task
    superclass. The subclasses are used to define required fields and special
    functionality.

"""

from time import time

from util.decorators import constant


class _Status(object):

    @constant
    def CREATED(self):
        """Task has been created but not yet posted."""
        return "created"

    @constant
    def POSTED(self):
        """Task has been posted to/from Foreman/Worker."""
        return "posted"

    @constant
    def ASSIGNED(self):
        """Task has been assigned to somebody to actually do."""
        return "assigned"

    @constant
    def COMPLETED(self):
        """The outlined work in this Task is complete but under
        review."""
        return "completed"

    @constant
    def APPROVED(self):
        """The work has been approved by the Employer and is closed
        out."""
        return "approved"

STATUS = _Status()


class Task(object):

    """A field list.

    Attributes
    ----------
    _current_synched_ts : `int`
        The timestamp of the current synch that is being processed.
    _worker : `ServiceWorker`
    _category : `str`
    _id : `int`
    _status : `str`
    _name : `str`
    _comments : {id, `Comment`}, optional
    _last_synched_ts : `int`, optional
        The timestamp of the last time a synch occurred with the service.
    _reciprocal_id : `int`, optional
        The Tasks's complementary Task's id.
    _description : `str`, optional
    _email : `str`, optional
    _price : `int`, optional
    _location : `int`, optional
        An id (currently using TaskRabbit's) that represents the city.

    """


    def __init__(self, category, id, name):
        self._current_synched_ts = int(time())
        self._category = category
        self._id = id
        self._status = None  # doesn't get created until it's in the DB
        self._name = name

        self._comments = {}
        self._last_synched_ts = None
        self._reciprocal_id = None
        self._description = None
        self._email = None
        self._price = None
        self._location = None


    def category(self):
        return self._category


    def id(self):
        return self._id


    def has_status(self):
        """If the Task has any status then return True."""
        return self._status is not None


    def is_created(self):
        return self._status == STATUS.CREATED


    def set_status_to_created(self):
        self._status = STATUS.CREATED


    def is_posted(self):
        return self._status == STATUS.POSTED


    def set_status_to_posted(self):
        self._status = STATUS.POSTED


    def is_assigned(self):
        return self._status == STATUS.ASSIGNED


    def set_status_to_assigned(self):
        self._status = STATUS.ASSIGNED


    def is_completed(self):
        return self._status == STATUS.COMPLETED


    def set_status_to_completed(self):
        self._status = STATUS.COMPLETED


    def is_approved(self):
        return self._status == STATUS.APPROVED


    def set_status_to_approved(self):
        self._status = STATUS.APPROVED


    def name(self):
        return self._name


    def get_comments(self):
        """Return a dict of Comments keyed on id."""
        return self._comments


    def set_comments(self, comments):
        """Set a dict of Comments keyed on id."""
        self._comments = comments


    def get_new_comments_list(self):
        """Return a list of Comments that have been created since the last
        synch time."""
        new_comments = [
                comment
                for comment in self.get_comments().values()
                if comment.created_ts() > self.last_synched_ts()
                ]

        return sorted(new_comments, key=lambda c: c.created_ts())


    def price(self):
        return self._price


    def set_price(self, price):
        if price:
            self._price = int(price)


    def email(self):
        return self._email


    def set_email(self, email):
        self._email = email


    def last_synched_ts(self):
        return self._last_synched_ts


    def set_last_synched_ts(self, last_synched_ts):
        if last_synched_ts:
            self._last_synched_ts = int(last_synched_ts)


    def push_current_to_last_synched(self):
        """Update the last synched ts to the current synch."""
        self.set_last_synched_ts(self._current_synched_ts)


    def reciprocal_id(self):
        return self._reciprocal_id


    def set_reciprocal_id(self, id):
        self._reciprocal_id = id


    def description(self):
        return self._description


    def set_description(self, description):
        self._description = description


    def location(self):
        return self._location


    def set_location(self, location_id):
        if location_id:
            self._location = int(location_id)


    def is_spec_ready(self):
        """If all required fields have values then return True."""
        required_fields = [a() for a in self.get_required_accessors()]
        return all(required_fields)


    def get_required_accessors(self):
        """Return a list of required fields' accessors."""
        return [
                self.id,
                self.name,
                ]


    def _print_task(self):
        print "\nTASK\n--------"
        print "id:", self._id
        print "name:", self._name
        print "price:", self._price
        print "email:", self._email
        print "category:", self._category
        print "reciprocal_id", self._reciprocal_id
        print "status:", self._status
        print "location:", self._location
        print "description:", self.description()
        print "spec ready?:", self.is_spec_ready()
        print ""


class RegistrationTask(Task):

    """The Task for registering new users with Jackalope. This Task uses
    SoloJob."""


    def get_required_accessors(self):
        """Return a list of required fields' accessors."""
        accessors = super(RegistrationTask, self).get_required_accessors()
        accessors.extend(
                [
                    self.email
                ])
        return accessors


class PricedTask(Task):

    """A Task that requires a price. This Task uses PairedJob."""


    def get_required_accessors(self):
        """Return a list of required fields' accessors."""
        accessors = super(PricedTask, self).get_required_accessors()
        accessors.extend(
                [
                    self.price
                ])
        return accessors


class TaskFactory(object):

    """Construct a Task with the subclass dependent on category."""

    REGISTRATION = unicode("registration")  # RegistrationTask
    PRICED = unicode("priced")  # PricedTask


    # Used to map string task categories with Task constructor functions.
    TASK_CATEGORY_MAPPING = {
            REGISTRATION: RegistrationTask,
            PRICED: PricedTask
            }


    @classmethod
    def instantiate_task(class_, category, task_id, name):
        task_constructor = class_.TASK_CATEGORY_MAPPING.get(category, Task)
        if type(task_constructor) == Task:
            print "oh yeah, we got one of them tasks"

        return task_constructor(category, task_id, name)
