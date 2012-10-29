"""
    urls
    ----

    URLs for the Tornado handlers.

"""
from handlers.mail import MailToHandler, MailFromHandler, MailAboutHandler


url_patterns = [
        (r"/mail/to/", MailToHandler),
        (r"/mail/from/", MailFromHandler),
        (r"/mail/about/", MailAboutHandler),
        ]
