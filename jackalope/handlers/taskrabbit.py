"""
    taskrabbit
    ----------

    Callback handlers for any notifications from Task Rabbit.

"""
from model.worker.task_rabbit_employee import TASK_RABBIT

from .vendor import TaskVendorHandler, CommentVendorHandler


class TaskRabbitTaskHandler(TaskVendorHandler):

    vendor = TASK_RABBIT.VENDOR


class TaskRabbitCommentHandler(CommentVendorHandler):

    vendor = TASK_RABBIT.VENDOR
