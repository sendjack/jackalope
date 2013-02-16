"""
    Mailgun Mailer
    --------------

    Send outgoing mail using requests, jutil, and mailgun.

"""

import requests

from jutil.decorators import constant


MAILGUN_API_URL = unicode("https://api.mailgun.net/v2")
MAILGUN_MESSAGES_SUFFIX = unicode("messages")

_mailgun_api_key = None
_mailgun_domain = None
_default_name = ""
_default_email = ""


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
    def TO(self):
        return "to"

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

    @constant
    def TEXT(self):
        return "text"

    @constant
    def API(self):
        return "api"

MAIL = _Mail()


def initialize(api_key, domain, name="", email=""):
    """Set the api key and domain for the mailgun account to use."""
    global _mailgun_api_key
    global _mailgun_domain
    global _default_name
    global _default_email

    _mailgun_api_key = api_key
    _mailgun_domain = domain
    _default_name = name
    _default_email = email


def send_message_from_jack(recipient, subject, body):
    """Send a smtp message using Mailgun's API with 'Jack Lope' as the sender
    and return the response dict.

    Parameters
    ----------
    recipient : `str`
        Formatted as "Name <email@domain.com>"
    subject : `str`
    body : `str`

    """
    return send_message(_get_default_sender, recipient, subject, body)


def send_message_as_jack(sender_email, recipient, subject, body):
    """Send a smtp mesage using Mailgun's API with 'Jack Lope' as
    the name and the sender_email as the email, and return the response dict.

    Parameters
    ----------
    sender_email `str`
    recipient : `str`
        Formatted as "Name <email@domain.com>"
    subject : `str`
    body : `str`

    """
    sender = _get_sender(_default_name, sender_email)
    return send_message(sender, recipient, subject, body)


def send_message(sender, recipient, subject, body):
    """Send a smtp message using Mailgun's API and return the response dict.

    Parameters
    ----------
    sender : `str`
        Formatted as "Name <email@domain.com>"
    recipient : `str`
        Formatted as "Name <email@domain.com>"
    subject : `str`
    body : `str`

    """
    data_dict = {
            MAIL.FROM: sender,
            MAIL.TO: [recipient],
            MAIL.SUBJECT: subject,
            MAIL.TEXT: body
            }
    url = unicode("{}/{}/{}").format(
            MAILGUN_API_URL,
            _mailgun_domain,
            MAILGUN_MESSAGES_SUFFIX)
    response = requests.post(
            url,
            auth=(MAIL.API, _mailgun_api_key),
            data=data_dict)

    return response.text


def _get_default_sender():
    return _get_sender(_default_name, _default_email())


def _get_sender(name, email):
    return unicode("{} <{}>").format(name, email)
