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

    @constant
    def TASK_ID(self):
        return "task_id"

    @constant
    def IS_FROM_CUSTOMER(self):
        return "is_from_customer"


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

    @constant
    def COMMENT_PATH(self):
        return "/a/comment"

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


    def request_required_fields(self, task):
        """Request unfilled but required fields."""
        # FIXME: Send Jack has no way to notify that they need additional
        # fields. Unless we send out an email...but that doesn't seem to be a
        # good idea.
        raise NotImplementedError(
                "SendJack cannot be notified that additiona fields are needed")
        return False


    def add_comment(self, task_id, message):
        """Create a comment in the service on a task."""
        comment_dict = {
                SEND_JACK_FIELD.TASK_ID: task_id,
                FIELD.MESSAGE: message,
                SEND_JACK_FIELD.IS_FROM_CUSTOMER: False
                }

        new_comment_dict = self._post(
                SEND_JACK.PROTOCOL,
                SEND_JACK.DOMAIN,
                SEND_JACK.COMMENT_PATH,
                comment_dict)

        return new_comment_dict is not None


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
