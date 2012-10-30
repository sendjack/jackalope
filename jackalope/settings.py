"""
    settings
    --------

    All application settings. A single point for environmental variable
    interactions.

"""

import os

from util import integer

# Make filepaths relative to settings.
path = lambda root, *a: os.path.join(root, *a)
ROOT = os.path.dirname(os.path.abspath(__file__))

# Generic Error messages
NOT_IMPLEMENTED_ERROR = "Subclass and override."
INIT_INTERFACE_ERROR = "Do not try to instantiate an interface."
DO_NOT_OVERRIDE = "Do not override this method."

# Asana
ASANA_API_KEY = os.environ.get("ASANA_API_KEY")
ASANA_JACK_USER_ID = integer.to_integer(os.environ.get("ASANA_JACK_USER_ID"))
TEST_WORKSPACE_ID = integer.to_integer(os.environ.get("TEST_WORKSPACE_ID"))
JACKALOPE_TAG_ID = integer.to_integer(os.environ.get("JACKALOPE_TAG_ID"))

# TaskRabbit
TASK_RABBIT_KEY = os.environ.get("TASK_RABBIT_KEY")
TASK_RABBIT_SECRET = os.environ.get("TASK_RABBIT_SECRET")
TASK_RABBIT_ACCESS_TOKEN = os.environ.get("TASK_RABBIT_ACCESS_TOKEN")
TASK_RABBIT_REDIRECT_URI = os.environ.get("TASK_RABBIT_REDIRECT_URI")

# Mailgun
MAILGUN_API_KEY = os.environ.get("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.environ.get("MAILGUN_DOMAIN")
