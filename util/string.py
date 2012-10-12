""" Module: string

A all-purpose module for working with strings.

"""


def to_string(anything):
    """ Convert anything into a string. Only difference between this function
    and str() is that 'NoneType' returns the empty string. """
    new_string = ""
    if anything is not None:
        new_string = str(anything)

    return new_string
