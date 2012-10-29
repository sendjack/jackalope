"""
    mail
    ----

    Handlers for incoming mail.

"""
import httplib
import tornado.web

from jackalope.errors import OverrideRequiredError, OverrideNotAllowedError
from jackalope.util.decorators import constant


DOMAIN = "app7972367.mailgun.org"
POSTMASTER_LOGIN = "postmaster"
POSTMASTER_PASSWORD = "6uug3km0ofv8"
TEST_LOGIN = "test"
TEST_PASSWORD = "themightypeacock"
API_URL = "https://api.mailgun.net/v2"
API_KEY = "key-82kpweabx72z6bmih2sa9xp6hqbv7b97"


class _Mail(object):

    """Mail constants for interacting with incoming mail from MailGun.

    http://documentation.mailgun.net/user_manual.html#receiving-messages

    """

    @constant
    def RECIPIENT(self):
        return "recipient"

    @constant
    def SENDER(self):
        return "sender"

    @constant
    def FROM(self):
        return "from"

    @constant
    def SUBJECT(self):
        return "subject"

    @constant
    def BODY(self):
        return "body-plain"

    @constant
    def BODY_HTML(self):
        return "body-html"

    @constant
    def STRIPPED_TEXT(self):
        return "stripped-text"

    @constant
    def STRIPPED_SIGNATURE(self):
        return "stripped-signature"

    @constant
    def STRIPPED_HTML(self):
        return "stripped-html"

    @constant
    def ATTACHMENT_COUNT(self):
        return "attachment-count"

    @constant
    def ATTACHMENT_X(self):
        return "attachment-x"

    @constant
    def TIMESTAMP(self):
        return "timestamp"

    @constant
    def TOKEN(self):
        return "token"

    @constant
    def SIGNATURE(self):
        return "signature"

    @constant
    def MESSAGE_HEADERS(self):
        return "message-headers"

    @constant
    def CONTENT_ID_MAP(self):
        return "content-id-map"

MAIL = _Mail()


class MailHandler(tornado.web.RequestHandler):

    """ Display the Deck. """


    def get(self):
        raise OverrideNotAllowedError()


    def post(self):
        raise OverrideRequiredError()


class MailToHandler(MailHandler):


    def post(self):
        # http://docs.python.org/2/library/httplib.html
        sender = self.get_argument(MAIL.SENDER)
        recipient = self.get_argument(MAIL.RECIPIENT)
        subject = self.get_argument(MAIL.SUBJECT)
        body = self.get_argument(MAIL.BODY)
        body_without_quotes = self.get_argument(MAIL.BODY_STRIPPED)

        print "\nMAIL\n--------"
        print "sender:", sender
        print "recipient:", recipient
        print "subject:", subject
        print "body:", body
        print "body w/o quotes:", body_without_quotes
        print ""

        # note: other MIME headers are also posted here...

        # attachments
        #for file in self.request.files:
        #    # do something with the file
        #    pass

        # returned text is ignored but HTTP status code matters. mailgun wants
        # to see 2xx, otherwise it will make another attempt in 5 minutes.
        self.set_status(httplib.OK)
        self.flush()
        self.finish()


class MailFromHandler(MailHandler):
    pass


class MailAboutHandler(MailHandler):
    pass
