"""
    errors
    ------

    Top-level application errors.

"""


class OverrideRequiredError(NotImplementedError):

    REASON = unicode("Subclass and override.")

    def __init__(self):
        super(OverrideRequiredError, self).__init__(self.REASON)


class OverrideNotAllowedError(NotImplementedError):

    REASON = unicode("This method cannot be overridden by a subclass.")

    def __init__(self, context=""):
        super(OverrideNotAllowedError, self).__init__(
                unicode("{} {}").format(self.REASON, context))


class InterfaceNotInstantiableError(OverrideNotAllowedError):

    REASON = unicode("Interfaces cannot be instantiated.")

    def __init__(self):
        super(InterfaceNotInstantiableError, self).__init__(self.REASON)
