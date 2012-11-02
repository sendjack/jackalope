"""
    mail
    ----

    Handlers for incoming mail.

"""

import hashlib
import hmac
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
    def BODY_TEXT(self):
        return "body-plain"

    @constant
    def BODY_HTML(self):
        return "body-html"

    @constant
    def BODY_TEXT_STRIPPED(self):
        return "stripped-text"

    @constant
    def BODY_HTML_STRIPPED(self):
        return "stripped-html"

    @constant
    def STRIPPED_SIGNATURE(self):
        return "stripped-signature"

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
        token = self.get_argument(MAIL.TOKEN)
        timestamp = self.get_argument(MAIL.TIMESTAMP)
        signature = self.get_argument(MAIL.SIGNATURE)
        if self.verify(API_KEY, token, timestamp, signature):
            self.process_request()
        else:
            raise UnverifiedMailRequest()


    def verify(self, api_key, token, timestamp, signature):
            return signature == hmac.new(
                    key=api_key,
                    msg='{}{}'.format(timestamp, token),
                    digestmod=hashlib.sha256).hexdigest()


    def process_request(self):
        raise OverrideRequiredError()


class MailToHandler(MailHandler):


    def process_request(self):
        # http://docs.python.org/2/library/httplib.html
        sender = self.get_argument(MAIL.SENDER)
        recipient = self.get_argument(MAIL.RECIPIENT)
        subject = self.get_argument(MAIL.SUBJECT)
        body = self.get_argument(MAIL.BODY_TEXT)
        body_without_quoted_text = self.get_argument(MAIL.BODY_TEXT_STRIPPED)

        print "\nMAIL\n--------"
        print "sender:", sender
        print "recipient:", recipient
        print "subject:", subject
        print "body:", body
        print "body w/o quotes:", body_without_quoted_text
        print ""

        # note: other MIME headers are also posted here...

        # attachments
        #for file in self.request.files:
        #    # do something with the file
        #    pass

        # returned text is ignored but HTTP status code matters. mailgun wants
        # to see 2xx, otherwise it will make another attempt in 5 minutes.
        # tornado finishes requests automatically


class MailFromHandler(MailHandler):
    pass


class MailAboutHandler(MailHandler):
    pass


class UnverifiedMailRequest(Exception):

    REASON = "Unverified mail request sent and caught."

    def __init__(self):
        super(UnverifiedMailRequest, self).__init__(self.REASON)
