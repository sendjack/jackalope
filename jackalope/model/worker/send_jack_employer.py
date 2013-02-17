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
        return "title"

    @constant
    def CUSTOMER_DESCRIPTION(self):
        return "customer_description"


SEND_JACK_FIELD = _SendJackField()


class _SendJack(object):

    @constant
    def SEND_JACK(self):
        return "send-jack"

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
        return SEND_JACK.SEND_JACK


    def read_task(self, task_id):
        path = unicode("{}/{}").format(
                SEND_JACK.TASK_PATH,
                task_id)
        raw_task = self._get(SEND_JACK.DOMAIN, path)

        transformer = SendJackTransformer()
        transformer.set_raw_task(raw_task)
        from pprint import pprint
        pprint(transformer.get_task())
        return self._ready_spec(transformer.get_task())


    def request_required_fields(self, task):
        """Request unfilled but required fields."""
        # FIXME: Send Jack has no way to notify that they need additional
        # fields.
        return False


class SendJackTransformer(TaskTransformer):


    def __init__(self):
        super(SendJackTransformer, self).__init__(None)


    def _get_field_name_map(self):
        field_name_map = super(
                SendJackTransformer,
                self)._get_field_name_map()
        field_name_map[FIELD.NAME] = SEND_JACK_FIELD.TITLE
        field_name_map[FIELD.DESCRIPTION] = (
                SEND_JACK_FIELD.CUSTOMER_DESCRIPTION)

        return field_name_map
