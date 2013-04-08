"""
    taskrabbit
    ----------

    Callback handlers for any notifications from Task Rabbit.

"""
from model.worker.transformer import FIELD
from model.worker.task_rabbit_employee import TASK_RABBIT, TASK_RABBIT_FIELD

from .vendor import TaskVendorHandler, CommentVendorHandler


class TaskRabbitTaskHandler(TaskVendorHandler):

    vendor = TASK_RABBIT.VENDOR


    def _process_request(self):
        if self._id is not None:
            self._foreman.send_jack_for_task(self.vendor, self._id)
        else:
            body = self._get_request_body()
            items = body.get(TASK_RABBIT_FIELD.ITEMS)
            for item in items:
                id = item.get(TASK_RABBIT_FIELD.TASK).get(FIELD.ID)
                self._foreman.send_jack_for_task(self.vendor, id)


class TaskRabbitCommentHandler(CommentVendorHandler):

    vendor = TASK_RABBIT.VENDOR
