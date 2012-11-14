"""
    errors
    ------

    Top-level application errors.

"""


class OverrideRequiredError(NotImplementedError):

    REASON = unicode(
            "This member must be overridden (usually with a subclass).")

    def __init__(self):
        super(OverrideRequiredError, self).__init__(self.REASON)


class OverrideNotAllowedError(NotImplementedError):

    REASON = unicode("This member cannot be overridden.")

    def __init__(self, context=""):
        super(OverrideNotAllowedError, self).__init__(
                unicode("{} {}").format(self.REASON, context))


class InterfaceNotInstantiableError(OverrideNotAllowedError):

    REASON = unicode("Interfaces cannot be instantiated.")

    def __init__(self):
        super(InterfaceNotInstantiableError, self).__init__(self.REASON)


class AlreadySetError(OverrideNotAllowedError):

    REASON = "Once set, it is considered final and uneditable."

    def __init__(self):
        super(AlreadySetError, self).__init__(self.REASON)
