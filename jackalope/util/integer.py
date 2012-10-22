"""
    integer
    -------

    An all-purpose module for working with integers.

"""


def to_integer(anything):
    """Convert *anything* to a string using `int()` but return None if
    None."""
    new_integer = None
    if anything is not None:
        new_integer = int(anything)

    return new_integer
