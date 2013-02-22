"""
    vendor
    ------

    Base handler for all vendor handlers to subclass. It should handle any
    notifications from the vendors.

"""
import json
import tornado.web

from model.foreman import Foreman
from model.comment import COMMENT


class VendorHandler(tornado.web.RequestHandler):

    """Handle incoming requests from vendors.

    Attributes:
    -----------
    id : str

    """

    def get(self, id=None):
        self.id = id
        self._process_request()


    def post(self, id=None):
        self.id = id
        self._process_request()


    def _process_request(self):
        raise NotImplementedError()


    def _get_request_parameters(self):
        return json.loads(self.request.body)


class TaskVendorHandler(VendorHandler):

    """Handle incoming task requests."""

    def _process_request(self):
        foreman = Foreman()
        foreman.send_jack_for_employer_task(self.vendor, self.id)


class CommentVendorHandler(VendorHandler):

    """Handle incoming comment requests."""

    def _process_request(self):
        body = self._get_request_parameters()
        message = body.get(COMMENT.MESSAGE)

        foreman = Foreman()
        foreman.ferry_comment(self.vendor, self.id, message)
