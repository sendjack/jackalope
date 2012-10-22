"""
    comment
    -------

    Comment is a message posted by a user on a Task. Jackalope uses this class
    to ferry messages between services.

"""


class Comment(object):

    """Contain a message posted by a user on a Task.

    Attributes
    ----------
    _id : `int`
    _created_ts : `int`
    _message : `str`

    """


    def __init__(self, id, created_ts, message):
        self._id = id
        self._created_ts = created_ts
        self._message = message


    def id(self):
        return self._id


    def created_ts(self):
        return self._created_ts


    def message(self):
        return self._message


    def _print_comment(self):
        print "COMMENT"
        print "id", self._id
        print "created_ts", self._created_ts
        print "msg", self._message
