"""
    client
    ----

    Generic client authorization and request constants.

"""
from jutil.decorators import constant


class _Request(object):

    """These constants define third-party API authorization protocol."""

    @constant
    def AUTH_HEADER(self):
        return "Authorization"

    @constant
    def OAUTH(self):
        return "OAuth "

    @constant
    def APP_HEADER(self):
        return "X-Client-Application"

    @constant
    def CONTENT_TYPE(self):
        return "Content-Type"

    @constant
    def APP_JSON(self):
        return "application/json"

REQUEST = _Request()
