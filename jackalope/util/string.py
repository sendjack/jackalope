"""
    string
    ------

    A all-purpose module for working with strings.

"""


def to_string(anything):
    """Convert *anything* to a string using `str()` but return an empty string
    if None."""
    new_string = ""
    if anything is not None:
        new_string = str(anything)

    return new_string
