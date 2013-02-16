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
from pprint import pprint

from jutil.decorators import constant
from jutil.base_type import to_integer, to_unicode


class _Field(object):

    @constant
    def STATUS(self):
        return "status"

    @constant
    def DESCRIPTION(self):
        return "description"

    @constant
    def EMAIL(self):
        return "email"

    @constant
    def PRICE(self):
        return "price"

    @constant
    def LOCATION(self):
        return "location"

FIELD = _Field()


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
    _category : `str`
    _id : `unicode`
    _name : `unicode`

    _properties : `dict`
    _comments : {id, `Comment`}, optional
    _updated : `bool`
        True if the Task has an updated property.

    """


    def __init__(self, category, id, name):
        self._category = category
        self._id = to_unicode(id)
        self._name = name

        # doesn't get created until it's in the DB
        self._properties = {}
        self._set_status(None)
        self.set_description(None)
        self.set_email(None)
        self.set_price(None)
        self.set_location(None)

        self._comments = {}

        self._updated = False


    def category(self):
        return self._category


    def id(self):
        return self._id


    def name(self):
        return self._name


    def has_status(self):
        """If the Task has any status then return True."""
        return self._get_status() is not None


    def is_created(self):
        return self._get_status() == STATUS.CREATED


    def set_status_to_created(self):
        self._set_status(STATUS.CREATED)


    def is_posted(self):
        return self._get_status() == STATUS.POSTED


    def set_status_to_posted(self):
        self._set_status(STATUS.POSTED)


    def is_assigned(self):
        return self._get_status() == STATUS.ASSIGNED


    def set_status_to_assigned(self):
        self._set_status(STATUS.ASSIGNED)


    def is_completed(self):
        return self._get_status() == STATUS.COMPLETED


    def set_status_to_completed(self):
        self._set_status(STATUS.COMPLETED)


    def is_approved(self):
        return self._get_status() == STATUS.APPROVED


    def set_status_to_approved(self):
        self._set_status(STATUS.APPROVED)


    def description(self):
        return self._get_property(FIELD.DESCRIPTION)


    def set_description(self, description):
        self._set_property(FIELD.DESCRIPTION, description)


    def price(self):
        return self._get_property(FIELD.PRICE)


    def set_price(self, price):
        int_price = to_integer(price)
        self._set_property(FIELD.PRICE, int_price)

    def email(self):
        return self._get_property(FIELD.EMAIL)


    def set_email(self, email):
        self._set_property(FIELD.EMAIL, email)


    def location(self):
        return self._get_property(FIELD.LOCATION)


    def set_location(self, location_id):
        int_location = to_integer(location_id)
        self._set_property(FIELD.LOCATION, int_location)


    def get_comments(self):
        """Return a dict of Comments keyed on id."""
        return self._comments


    def set_comments(self, comments):
        """Set a dict of Comments keyed on id."""
        self._comments = comments


    def get_comments_since_ts(self, synched_ts):
        """Return a list of Comments that have been created since the last
        synch time."""
        new_comments = [
                comment
                for comment in self.get_comments().values()
                if comment.created_ts() > synched_ts
                ]

        return sorted(new_comments, key=lambda c: c.created_ts())


    def is_updated(self):
        """Return True if the Task has been updated since creation."""
        return self._updated


    def reset_updated(self):
        """Reset's the Task's updated state to False."""
        self._updated = False


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
        task_dict = {
                "id": self.id(),
                "name": self.name(),
                "category": self.category(),
                "price": self.price(),
                "email": self.email(),
                "status": self._get_status(),
                "location": self.location(),
                "description": self.description(),
                "spec ready?": self.is_spec_ready(),
                "updated?": self.is_updated()
                }

        pprint(task_dict)


    def _get_property(self, key):
        return self._properties.get(key)


    def _set_property(self, key, value):
        self._properties[key] = value
        self._updated = True
        return self._properties.get(key)


    def _get_status(self):
        return self._get_property(FIELD.STATUS)


    def _set_status(self, status):
        self._set_property(FIELD.STATUS, status)


class RegistrationTask(Task):

    """The Task for registering new users with Jackalope. This Task uses
    SoloWorkflow."""


    def get_required_accessors(self):
        """Return a list of required fields' accessors."""
        accessors = super(RegistrationTask, self).get_required_accessors()
        accessors.extend([
                self.email,
                ])
        return accessors


class PricedTask(Task):

    """A Task that requires a price. This Task uses PairedWorkflow."""


    def get_required_accessors(self):
        """Return a list of required fields' accessors."""
        accessors = super(PricedTask, self).get_required_accessors()
        accessors.extend([
                self.price,
                self.description,
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
        task_constructor = class_.TASK_CATEGORY_MAPPING.get(
                category,
                PricedTask)
        if type(task_constructor) == Task:
            print "Task, Abstract Superclass instantiated."

        return task_constructor(category, task_id, name)
