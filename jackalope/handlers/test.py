"""
    test
    ----

    A bunch of handlers for testing different functionality through a browser
    url.

"""
import tornado.web

from model.foreman import Foreman


class ForemanHandler(tornado.web.RequestHandler):

    def get(self, id=None):
        foreman = Foreman()
        foreman.send_jack()
