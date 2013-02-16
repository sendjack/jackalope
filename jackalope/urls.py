"""
    urls
    ----

    URLs for the Tornado handlers.

"""
from handlers.sendjack import SendJackTaskHandler
from handlers.taskrabbit import TaskRabbitCommentHandler


url_patterns = [
        (r"/sendjack/task", SendJackTaskHandler),
        (r"/taskrabbit/comment", TaskRabbitCommentHandler),
        ]
