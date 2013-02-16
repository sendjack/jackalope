"""
    vendor
    ------

    Base handler for all vendor handlers to subclass. It should handle any
    notifications from the vendors.

"""
import json
import tornado.web

#from jutil.decorators import constant



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
        print(self.vendor)
        print(self._get_request_parameters())


    def _get_request_parameters(self):
        return json.loads(self.request.body)
