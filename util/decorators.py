"""
    decorators
    ~~~~~~~~~~

    General purpose decorators.

"""


def constant(f):
    """Convert function to a constant variable."""


    def fset(self, value):
        """Overload constant function's set to make final."""
        raise SyntaxError


    def fget(self):
        """Overload constant function's get."""
        return f(self)

    return property(fget, fset)
