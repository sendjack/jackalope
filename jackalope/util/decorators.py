"""
    decorators
    ----------

    General purpose decorators.

"""

from base_type import ByteError


def constant(f):

    """Convert function to a constant variable."""


    def fset(self, value):
        """Overload constant function's set to make final."""
        raise SyntaxError


    def fget(self):
        """Overload constant function's get."""
        value = f(self)

        if type(value) is int or type(value) is unicode:
            pass
        elif type(value) is str:
            value = unicode(value)
        else:
            raise ByteError()

        return value

    return property(fget, fset)
