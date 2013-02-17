"""
    test
    ----

    A bunch of handlers for testing different functionality through a browser
    url.

"""
import tornado.web

#from model.foreman import Foreman
from model.worker.send_jack_employer import SendJackEmployer


class ForemanHandler(tornado.web.RequestHandler):

    def get(self, id=None):
        worker = SendJackEmployer()
        task = worker.read_task(id)

        print task
        if task is not None:
            self.write(task)
        else:
            self.write("task was none")
        #foreman = Foreman()
        #foreman.send_jack()
