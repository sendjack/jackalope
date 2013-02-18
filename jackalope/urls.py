"""
    urls
    ----

    URLs for the Tornado handlers.

"""
from handlers.sendjack import SendJackTaskHandler, SendJackCommentHandler
from handlers.taskrabbit import TaskRabbitTaskHandler, TaskRabbitCommentHandler
from handlers.foreman import ForemanHandler


url_patterns = [
        (r"/sendjack/task/?([0-9]+)?", SendJackTaskHandler),
        (r"/sendjack/task/?([0-9]+)?", SendJackCommentHandler),
        (r"/taskrabbit/task/?([0-9]+)?", TaskRabbitTaskHandler),
        (r"/taskrabbit/comment/?([0-9]+)?", TaskRabbitCommentHandler),
        (r"/jackalope", ForemanHandler),
        ]
