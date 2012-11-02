#!/usr/bin/env python
"""
    Jackalope Mail Receiver
    -----------------------

    A process for receiving mail trigger's from worker services.

"""

import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.options import options

from settings import settings
from urls import url_patterns


class MailReceiver(tornado.web.Application):

    """The Tornado instance for receiving mail triggers."""


    def __init__(self):
        tornado.web.Application.__init__(self, url_patterns, **settings)


def main():
    app = MailReceiver()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
