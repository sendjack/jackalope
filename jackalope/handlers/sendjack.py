"""
    sendjack
    --------

    Callback handlers for any notifications from sendjack.

"""
from model.worker.send_jack_employer import SEND_JACK

from .vendor import TaskVendorHandler, CommentVendorHandler


class SendJackTaskHandler(TaskVendorHandler):

    vendor = SEND_JACK.VENDOR


class SendJackCommentHandler(CommentVendorHandler):

    vendor = SEND_JACK.VENDOR
