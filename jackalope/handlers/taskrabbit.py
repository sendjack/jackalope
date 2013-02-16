"""
    taskrabbit
    ----------

    Callback handlers for any notifications from Task Rabbit.

"""
from vendor import VendorHandler


class TaskRabbitCommentHandler(VendorHandler):

    def _process_request(self):
        print(self.id)
