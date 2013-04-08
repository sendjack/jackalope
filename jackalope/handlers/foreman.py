"""
    foreman
    ----

    Handle incoming requests to check all tasks.

"""
import tornado.web

from model.foreman import Foreman


class ForemanHandler(tornado.web.RequestHandler):

    def get(self):
        foreman = Foreman()
        foreman.send_jack()
