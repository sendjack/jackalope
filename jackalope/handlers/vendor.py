"""
    vendor
    ------

    Base handler for all vendor handlers to subclass. It should handle any
    notifications from the vendors.

    TODO: This hierarchy is temporary until we merge in the CRUDHandler
    hierarchy. Then this hierarchy will translate/transform from quirky vendor
    interfaces into our well defined format.

"""
import json
import tornado.web

from model.foreman import Foreman
from model.comment import COMMENT


class VendorHandler(tornado.web.RequestHandler):

    """Handle incoming requests from vendors.

    Attributes:
    -----------
    vendor : str
    _id : str
    _foreman : Foreman

    """

    def initialize(self):
        self._foreman = Foreman()


    def get(self, id=None):
        self._id = id
        self._process_request()


    def post(self, id=None):
        self._id = id
        self._process_request()


    def _process_request(self):
        raise NotImplementedError()


    def _get_request_body(self):
        return json.loads(self.request.body)


class TaskVendorHandler(VendorHandler):

    """Handle incoming task requests."""

    def _process_request(self):
        self._foreman.send_jack_for_task(self.vendor, self._id)


class CommentVendorHandler(VendorHandler):

    """Handle incoming comment requests."""

    def _process_request(self):
        body = self._get_request_body()
        message = body.get(COMMENT.MESSAGE)

        self._foreman.ferry_comment(self.vendor, self._id, message)
