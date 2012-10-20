""" Module: base

ServiceWorker is the base class for all interactions with external service's
APIs. Employer (ServiceWorker) handles interactions with task doer type
services and Employee (ServiceWorker) handles interactions with project
management type services. Each service/API will have its own subclass.

ServiceWorker is on a Transformer to handle mappings between the service and
our Task object.

ServiceWorker also provides the public facing API that the Foreman/Job can use
to interact with external services.

"""
import xml.etree.cElementTree as ET
from copy import deepcopy

from util.decorators import constant
from util import string
import settings
from task import TaskFactory


class _Field(object):

    """ Constants for accessing and setting task dictionaries. """

    @constant
    def ID(self):
        return "id"

    @constant
    def NAME(self):
        return "name"

    @constant
    def PRICE(self):
        return "price"

    @constant
    def EMAIL(self):
        return "email"

    @constant
    def DESCRIPTION(self):
        return "description"

    @constant
    def RECIPROCAL_ID(self):
        return "reciprocal_id"

    @constant
    def CATEGORY(self):
        return "category"

    @constant
    def LOCATION(self):
        return "location"

    @constant
    def STATUS(self):
        return "status"

FIELD = _Field()


class _Value(object):

    """ Constants for setting task dictionary values. """

    @constant
    def POSTED(self):
        return "posted"

    @constant
    def ASSIGNED(self):
        return "assigned"

    @constant
    def COMPLETED(self):
        return "completed"

    @constant
    def APPROVED(self):
        return "approved"

VALUE = _Value()


class ServiceWorker(object):

    """ Abstract superclass for connecting to external apis. """


    def __init__(self):
        """ Construct ServiceWorker. """
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)


    def create_task(self, worker_task):
        """ Use a Worker's Task to create a task in the Worker's Service.

        Required:
        Task worker_task    the Worker's Task.

        Return:
        Task - the new Task

        """
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)


    def read_task(self, task_id):
        """ Connect to Worker's service and return the requested Task."""
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)


    def read_tasks(self):
        """ Connect to Worker's service and return all tasks.

        Return:
        dict    all the Tasks keyed on id

        """
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)


    def update_task(self, task):
        """ Connect to Worker's service and udpate the task.

        Required:
        Task task   The Task to update.

        Return:
        Task - updated Task.

        """
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)


    def request_fields(self, task):
        """ Request from the service additional fields. """
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)


    def update_task_to_posted(self, task):
        """ Update the service's task's status to POSTED and return this
        updated Task.

        Required:
        Task task   The Task to update.

        Return:
        Task - udpated Task.

        """
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)


    def update_task_to_assigned(self, task):
        """ Update the service's task's status to ASSIGNED and return this
        updated Task.

        Required:
        Task task   The Task to update.

        Return:
        Task - udpated Task.

        """
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)


    def update_task_to_completed(self, task):
        """ Update the service's task's status to COMPLETED and return this
        updated Task.

        Required:
        Task task   The Task to update.

        Return:
        Task - udpated Task.

        """
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)


    def update_task_to_approved(self, task):
        """ Update the service's task's status to APPROVED and return this
        updated Task.

        Required:
        Task task   The Task to update.

        Return:
        Task - udpated Task.

        """
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)


    def _get(self, path):
        """ Connect to a service with a GET request.

        Required:
        str     path to desired action

        Return:
        str     The parsed response

        """
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)


    def _post(self, path, data):
        """ Connect to a service with a POST request.

        Required:
        str     path to desired action
        str     data to post

        Return:
        str     The parsed response

        """
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)


    def _ready_spec(self, task):
        """ Check to make sure task has a ready spec before handing it over to
        the Foreman. """
        if not task.is_spec_ready():
            self.request_required_fields(task)
            task = None
            print "spec incomplete"

        return task


    # FIXME: produce_dict and retrieve_id are clearly part of Transformer.
    def _produce_dict(self, raw_tasks):
        """ Convert the list of raw tasks into a dict keyed on 'id'. """
        return {self._retrieve_id(t): t for t in raw_tasks}


    def _retrieve_id(self, raw_task):
        """ Get the 'id' from the raw_task. """
        # FIXME: This needs to got through the field map
        return raw_task[FIELD.ID]



class Employer(ServiceWorker):

    """ Abstract superclass for interacting with Employer (e.g., project
    management services. """


    def __init__(self):
        """ Construct Employer. """
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)


class Employee(ServiceWorker):

    """ Abstract superclass for interacting with Employee (e.g., task doers)
    services."""


    def __init__(self):
        """ Construct Employee. """
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)



class Transformer(object):

    """ Handle parsing the service's response dictionary to construct a Task
    and deconstructing a Task into a raw task dictionary for the service.

    Required:
    str _embedding_field        The field to use to embed other fields.

    Optional:
    Task _task      Once the Transformer has been used it stores the Task for
                    further access.
    dict _raw_task  Once the Transformer has been used it stores the Task's
                    dict for further access.

    """


    def __init__(self, embedding_field=None):
        """ Construct a Transformer. """
        self._embedding_field = embedding_field

        self._task = None
        self._raw_task = None


    def get_task(self):
        """ Return the set task or construct it from the raw_task. """
        task = None
        if self._task:
            task = self._task
        elif self._raw_task:
            task = self._construct_task_from_dict()
        else:
            raise BadTransformationError()

        return task


    def set_task(self, task):
        """ Set the Task for this Transformation and make it uneditable. """
        if self._task or self._raw_task:
            raise BadTransformationError()
        else:
            self._task = task


    def get_raw_task(self):
        """ Return the raw task dict or deconstruct it from task. """
        raw_task = None
        if self._raw_task:
            raw_task = self._raw_task
        elif self._task:
            raw_task = self._deconstruct_task_to_dict()
        else:
            raise BadTransformationError()

        return raw_task


    def set_raw_task(self, raw_task):
        """ Set the raw task dict for this Transformation and make it
        uneditable. """
        if self._raw_task or self._task:
            raise BadTransformationError()
        else:
            self._raw_task = raw_task


    def get_embedded_field_value(self):
        """ Return the value of the Task's embedded field. """
        return self.get_raw_task().get(self._embedding_field)


    def transform_accessors_to_fields(self, task, accessors):
        """ Transform a list of accessors to a list of fields (str). """
        return [
                self._get_service_field_name_from_accessor(task, a)
                for a in accessors
                ]


    def _construct_task_from_dict(self):
        """ Construct Task from the raw task.

        Return:
        Task The Task built from the raw task.

        """
        raw_task = deepcopy(self._raw_task)

        # flatten raw task dict
        raw_task = self._flatten_raw_task(raw_task)

        # build task
        if not raw_task.get(self._get_service_field_name(FIELD.ID)):
            print raw_task
        id = raw_task[self._get_service_field_name(FIELD.ID)]
        name = raw_task[self._get_service_field_name(FIELD.NAME)]
        # TODO: and what will happen if Cateogry is None?
        category = raw_task.get(self._get_service_field_name(FIELD.CATEGORY))

        task = TaskFactory.instantiate_task(category, id, name)
        self._populate_task(task, raw_task)

        return task


    def _deconstruct_task_to_dict(self):
        """ Deconstruct Task into a raw task dict and return it. """

        # turn task into dict
        raw_task = {}
        raw_task = self._populate_raw_task(raw_task, self._task)

        # unflatten raw task dict
        raw_task = self._unflatten_raw_task(raw_task)

        return raw_task


    def _flatten_raw_task(self, raw_task):
        """ Pop embedding field, extract embedded fields, and update raw task
        dict. """
        # extract embedded
        embedded_fields_dict = {}
        for jack_field_name in self._embedded_fields():
            service_field = self._get_service_field_name(jack_field_name)
            embedded = self._extract_embedded_field(raw_task, service_field)
            embedded_fields_dict[service_field] = embedded

        # remove embedding field and update
        raw_task.pop(self._embedding_field, None)
        raw_task.update(embedded_fields_dict)

        # interact with service in quircky ways to generate additional fields
        raw_task = self._pull_service_quirks(raw_task)

        return raw_task


    def _unflatten_raw_task(self, raw_task):
        """ Insert embedded fields into embedding field, remove those fields
        from the dict, and add the new embedding field to the dict. """
        # interact with service in quirky ways to generate additional fields
        raw_task = self._push_service_quirks(raw_task)

        # pop embedded fields and insert them into embedding value
        if self._embedding_field:
            embedding_value = ""
            for jack_field_name in self._embedded_fields():
                service_field = self._get_service_field_name(jack_field_name)
                value = raw_task.pop(service_field, None)
                embedding_value = self._insert_embedded_field(
                        embedding_value,
                        service_field,
                        value)

            # add embedding field, remove embedded fields
            raw_task[self._embedding_field] = embedding_value

        return raw_task


    def _pull_service_quirks(self, raw_task):
        """ Interact with the service in very service specific ways to pull
        additional fields into the raw task. """
        return raw_task


    def _push_service_quirks(self, raw_task):
        """ Interact with the service in very service specific ways to push
        fields back into their proper spot. """
        return raw_task


    def _populate_task(self, task, raw_task):
        """ Add the rest of the fields form the raw task to the Task.

        Required:
        Task task           The Task to finish constructing.
        dict raw_task       The dict to pull fields from

        Return:
        Task The Task built from the raw task.

        """
        for field_name in self._get_field_names():
            id_cond = field_name != FIELD.ID
            name_cond = field_name != FIELD.NAME
            category_cond = field_name != FIELD.CATEGORY
            status_cond = field_name != FIELD.STATUS
            if id_cond and name_cond and category_cond and status_cond:
                service_field_name = self._get_service_field_name(field_name)
                mutator = self._get_mutator_from_jack_field_name(
                        task,
                        field_name)

                mutator(raw_task.get(service_field_name))

        # add status info to task
        print "status processing in populate task"
        print self._get_service_field_name(FIELD.STATUS)
        status = raw_task.get(self._get_service_field_name(FIELD.STATUS))
        if status == VALUE.POSTED:
            task.set_status_to_posted()
        elif status == VALUE.ASSIGNED:
            task.set_status_to_assigned()
        elif status == VALUE.COMPLETED:
            task.set_status_to_completed()
        elif status == VALUE.APPROVED:
            task.set_status_to_approved()
        else:
            print "odd status"
            print "status", status

        return task


    def _populate_raw_task(self, raw_task, task):
        """ Grabs fields from the Task and updates the raw task dict. """
        for field_name in self._get_field_names():
            if field_name != FIELD.STATUS:
                service_field_name = self._get_service_field_name(field_name)
                accessor = self._get_accessor_from_jack_field_name(
                        task,
                        field_name)
                raw_task[service_field_name] = accessor()

        # add status info to raw task
        status = None
        if task.is_posted():
            status = VALUE.POSTED
        elif task.is_assigned():
            status = VALUE.ASSIGNED
        elif task.is_completed():
            status = VALUE.COMPLETED
        elif task.is_approved():
            status = VALUE.APPROVED
        raw_task[self._get_service_field_name(FIELD.STATUS)] = status

        return raw_task


    def _embedded_fields(self):
        """ A list of embedded fields for this service. """
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)


    def _extract_embedded_field(self, raw_task, service_field):
        """ Extract the embedded field and return it. """
        embedding_field_value = raw_task.get(self._embedding_field)
        et_elem = self._convert_blob_to_xml(embedding_field_value)
        et_elem = et_elem.find(service_field)

        text = None
        if et_elem is not None:
            if et_elem.text is not None:
                text = et_elem.text.strip()

        return text


    def _insert_embedded_field(
            self,
            embedding_field_value,
            service_field,
            value):
        """ Embed the field, value in to the raw_task's embedding value. """
        et_elem = ET.Element(service_field)
        et_elem.text = string.to_string(value)
        embedded_field_value = ET.tostring(et_elem, "utf-8", "html")

        return "{}\n{}".format(
                embedding_field_value,
                embedded_field_value)


    def _get_field_names(self):
        """ Return a list of Jackalope field names. """
        return [field for field in self._get_field_name_map().keys()]


    def _get_service_field_name(self, jack_field_name):
        """ Converts Jackalope's field name to the service's field name for
        accessing the raw task dictionary.

        Required:
        str jack_field_name - the field name that we use.

        Return:
        str service's field name.

        """
        return self._get_field_name_map()[jack_field_name]


    def _get_service_field_name_from_accessor(self, task, accessor):
        """ Converts the task's accessor to the service's field name.

        Required:
        Task task - the task whose accessor should be used as a key.
        function accessor - the Task's accessor to the field.

        Return:
        str - the service's field name.

        """
        accessor_to_field_name_dict = {
                tuple[0]: field_name
                for field_name, tuple
                in self._get_field_task_property_map(task).items()
                }
        field_name = accessor_to_field_name_dict[accessor]
        return self._get_service_field_name(field_name)


    def _get_accessor_from_jack_field_name(self, task, jack_field_name):
        """ Converts Jackalope field name to accessor.

        Required:
        Task task - the Task whose accessor should be returned.
        str jack_field_name - the name that we use.

        Return:
        function - accessor to Task's field.

        """
        (accessor, mutator) = self._get_field_task_property_map(task)[
                jack_field_name]
        return accessor


    def _get_mutator_from_jack_field_name(self, task, jack_field_name):
        """ Converts Jackalope field name to mutator.

        Required:
        Task task - the Task whose mutator should be returned.
        str jack_field_name - the name that we use.

        Return:
        function - mutator to Task's field.

        """
        (accessor, mutator) = self._get_field_task_property_map(task)[
                jack_field_name]
        return mutator


    def _get_field_name_map(self):
        """ Return a dict keyed on Jackalope's field name and valued on the
        service's field name. """
        return {
                FIELD.CATEGORY: FIELD.CATEGORY,
                FIELD.ID: FIELD.ID,
                FIELD.NAME: FIELD.NAME,
                FIELD.PRICE: FIELD.PRICE,
                FIELD.EMAIL: FIELD.EMAIL,
                FIELD.DESCRIPTION: FIELD.DESCRIPTION,
                FIELD.RECIPROCAL_ID: FIELD.RECIPROCAL_ID,
                FIELD.LOCATION: FIELD.LOCATION,
                FIELD.STATUS: FIELD.STATUS
                }


    def _get_field_task_property_map(self, task):
        """ Return a dict keyed on field name and valued by a tuple, (accessor,
        mutator). """
        return {
                FIELD.CATEGORY: (task.category, None),
                FIELD.ID: (task.id, None),
                FIELD.NAME: (task.name, None),
                FIELD.PRICE: (task.price, task.set_price),
                FIELD.EMAIL: (task.email, task.set_email),
                FIELD.DESCRIPTION: (task.description, task.set_description),
                FIELD.RECIPROCAL_ID: (
                        task.reciprocal_id,
                        task.set_reciprocal_id),
                FIELD.LOCATION: (task.location, task.set_location)
                }


    @staticmethod
    def _convert_blob_to_xml(field):
        """ Converts a field to xml by wrapping it in xml tags. """
        return ET.XML("<blob>{}</blob>".format(field))


class BadTransformationError(Exception):

    """ Raise this Exception when Transformer is not being used correctly. """

    def __init__(self):
        """ Construct a BadTransformationError. """
        self.reason = "Don't use Transformer like that."
