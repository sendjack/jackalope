"""
    Mailgun Mailer
    --------------

    Send outgoing mail using requests and mailgun. This is a basic
    implementation to test integration.

"""

import requests

import os


MAILGUN_API_KEY = os.environ.get("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.environ.get("MAILGUN_DOMAIN")
MAILGUN_API_URL = "https://api.mailgun.net/v2"
MAILGUN_MESSAGES_SUFFIX = "messages"

FROM = "from"
TO = "to"
SUBJECT = "subject"
TEXT = "text"
API = "api"

SENDER = "Jack A. Lope <jack@sendjack.com>"


def main():

    recipient = "Test <admin@sendjack.com>"
    subject = "Jack's not feeling so well."
    body = "You guys are the worst. Where the hell is my chicken soup?\n"
    body = body + (
            "Send through python, from mailgun. (yeah, that's how i roll.)"
            )

    send_simple_message(recipient, subject, body)


def send_simple_message(recipient, subject, body):
    """Send a smtp message using Mailgun's API and return the response dict.

    Parameters
    ----------
    recipient : `str`
        Formatted as "Name <email@domain.com>"
    subject : `str`
    body : `str`

    """
    data_dict = {
            FROM: SENDER,
            TO: [recipient],
            SUBJECT: subject,
            TEXT: body
            }
    url = "{}/{}/{}".format(
            MAILGUN_API_URL,
            MAILGUN_DOMAIN,
            MAILGUN_MESSAGES_SUFFIX)
    response = requests.post(
            url,
            auth=(API, MAILGUN_API_KEY),
            data=data_dict)

    return response.text
