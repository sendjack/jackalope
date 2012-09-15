""" Module: settings

All settings for the app. The only file that should interact with the
environmental variables.

"""
import os

# Make filepaths relative to settings.
path = lambda root, *a: os.path.join(root, *a)
ROOT = os.path.dirname(os.path.abspath(__file__))

# Generic Error messages
NOT_IMPLEMENTED_ERROR = "Subclass and override."


# Settings
ASANA_API_KEY = os.environ.get("ASANA_API_KEY")
TEST_WORKSPACE_ID = int(os.environ.get("TEST_WORKSPACE_ID"))
JACKALOPE_TAG_ID = int(os.environ.get("JACKALOPE_TAG_ID"))