"""
    urls
    ----

    URLs for the Tornado handlers.

"""
from handlers.sendjack import SendJackTaskHandler
from handlers.taskrabbit import TaskRabbitCommentHandler
from handlers.test import ForemanHandler


url_patterns = [
        (r"/sendjack/task/?([0-9]+)?", SendJackTaskHandler),
        (r"/taskrabbit/comment/?([0-9]+)?", TaskRabbitCommentHandler),
        (r"/", ForemanHandler),
        ]
