"""
    send_jack_employer
    ------------------

    Connect to sendjack.com and transform SendJack's tasks into Jackalope
    tasks.

"""
from jutil.decorators import constant
from jutil import environment

from .worker import Employer
from .transformer import TaskTransformer, FIELD


class _SendJackField(object):

    """Constants for the Send Jack dictionary field."""

    @constant
    def TITLE(self):
        return "customer_title"

    @constant
    def CUSTOMER_DESCRIPTION(self):
        return "customer_description"


SEND_JACK_FIELD = _SendJackField()


class _SendJack(object):

    @constant
    def VENDOR(self):
        return "send_jack"

    @constant
    def VENDOR_IN_HTML(self):
        return "sendjack"

    @constant
    def PROTOCOL(self):
        return "http"

    @constant
    def DOMAIN(self):
        return environment.get_unicode(unicode("SEND_JACK_DOMAIN"))

    @constant
    def TASK_PATH(self):
        return "/a/task"

SEND_JACK = _SendJack()


class SendJackEmployer(Employer):

    def __init__(self):
        self._headers = {}


    def name(self):
        return SEND_JACK.VENDOR


    def read_task(self, task_id):
        path = unicode("{}/{}").format(
                SEND_JACK.TASK_PATH,
                task_id)
        raw_task = self._get(SEND_JACK.PROTOCOL, SEND_JACK.DOMAIN, path)

        transformer = SendJackTaskTransformer()
        transformer.set_raw_task(raw_task)
        return self._ready_spec(transformer.get_task())


    def read_tasks(self):
        raise NotImplementedError()


    def update_task(self, task):
        transformer = SendJackTaskTransformer()
        transformer.set_task(task)
        raw_task_dict = transformer.get_raw_task()

        path = unicode("{}/{}").format(SEND_JACK.TASK_PATH, task.id())
        updated_task_dict = self._put(
                SEND_JACK.PROTOCOL,
                SEND_JACK.DOMAIN,
                path,
                raw_task_dict)

        updated_transformer = SendJackTaskTransformer()
        updated_transformer.set_raw_task(updated_task_dict)

        return self._ready_spec(updated_transformer.get_task())


    def update_task_to_created(self, task):
        # Don't do anything here because Send Jack already has the status as
        # created
        task.set_status_to_created()

        return task


    def update_task_to_posted(self, task):
        task.set_status_to_posted()
        updated_task = self.update_task(task)
        # self.add_comment(task.id(), Phrase.task_posted_note)

        return updated_task


    def update_task_to_assigned(self, task):
        task.set_status_to_assigned()
        updated_task = self.update_task(task)
        # self.add_comment(task.id(), Phrase.task_assigned_note)

        return updated_task


    def update_task_to_completed(self, task):
        task.set_status_to_completed()
        updated_task = self.update_task(task)
        #self.add_comment(task.id(), Phrase.task_completed_note)

        return updated_task


    def request_required_fields(self, task):
        """Request unfilled but required fields."""
        # FIXME: Send Jack has no way to notify that they need additional
        # fields. Unless we send out an email...but that doesn't seem to be a
        # good idea.
        raise NotImplementedError(
                "SendJack cannot be notified that additiona fields are needed")
        return False


    def add_comment(self, task_id, message):
        # FIXME: This does nothing and it should.
        return False


    def read_comments(self, task_id):
        # FIXME: This does nothing and it should.
        return {}


class SendJackTaskTransformer(TaskTransformer):


    def __init__(self):
        super(SendJackTaskTransformer, self).__init__(None)


    def _get_field_name_map(self):
        field_name_map = super(
                SendJackTaskTransformer,
                self)._get_field_name_map()
        field_name_map[FIELD.NAME] = SEND_JACK_FIELD.TITLE
        field_name_map[FIELD.DESCRIPTION] = (
                SEND_JACK_FIELD.CUSTOMER_DESCRIPTION)

        return field_name_map
