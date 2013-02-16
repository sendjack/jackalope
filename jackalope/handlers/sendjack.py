"""
    sendjack
    --------

    Callback handlers for any notifications from sendjack.

"""
from vendor import VendorHandler


class SendJackTaskHandler(VendorHandler):

    def _process_request(self):
        print(self.id)
