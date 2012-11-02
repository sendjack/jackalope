"""
    mail
    ----

    Handlers for incoming mail.

"""

import hashlib
import hmac
import re
import tornado.web

from jackalope.errors import OverrideRequiredError, OverrideNotAllowedError
from jackalope.util import string, integer
from jackalope.mailer import MAIL
from jackalope.mailer import MAILGUN_API_KEY as API_KEY
from jackalope.foreman import Foreman


#POSTMASTER_LOGIN = "postmaster"
#POSTMASTER_PASSWORD = "6uug3km0ofv8"
#TEST_LOGIN = "test"
#TEST_PASSWORD = "themightypeacock"


class MailHandler(tornado.web.RequestHandler):

    """ Display the Deck. """


    def get(self):
        raise OverrideNotAllowedError()


    def post(self):
        token = self.get_argument(MAIL.TOKEN)
        timestamp = self.get_argument(MAIL.TIMESTAMP)
        signature = self.get_argument(MAIL.SIGNATURE)
        if self.verify(API_KEY, token, timestamp, signature):
            self._process_request()
        else:
            raise UnverifiedMailRequestError()


    def verify(self, api_key, token, timestamp, signature):
            return signature == hmac.new(
                    key=api_key,
                    msg='{}{}'.format(timestamp, token),
                    digestmod=hashlib.sha256).hexdigest()


    def _process_request(self):
        raise OverrideRequiredError()


class MailToHandler(MailHandler):

    email_regex = r"(.+)\-(\d+)@"
    email_pattern = re.compile(email_regex)


    def _process_request(self):
        # http://docs.python.org/2/library/httplib.html
        sender = self.get_argument(MAIL.SENDER)
        recipient = self.get_argument(MAIL.RECIPIENT)
        subject = self.get_argument(MAIL.SUBJECT, "")
        # body = self.get_argument(MAIL.BODY_TEXT)
        # recent body text; not html; no quoted next; no signature
        most_recent_body = self.get_argument(MAIL.BODY_TEXT_STRIPPED)
        stripped_signature = self.get_argument(MAIL.STRIPPED_SIGNATURE, "")

        print "\nMAIL\n--------"
        print "sender:", sender
        print "recipient:", recipient
        print "subject:", subject

        match = self.email_pattern.match(recipient)
        service = string.to_string(match.group(1))
        task_id = integer.to_integer(match.group(2))

        if service and task_id:
            foreman = Foreman()
            message = "{}:\n{}\n{}".format(
                    subject,
                    most_recent_body,
                    stripped_signature)
            message = message.strip()
            foreman.ferry_comment(service, task_id, message)

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


class UnverifiedMailRequestError(Exception):

    REASON = "Unverified mail request sent and caught."

    def __init__(self):
        super(UnverifiedMailRequestError, self).__init__(self.REASON)
