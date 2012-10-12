""" Module: phrase

A collection of phrases (e.g. copy, text) to use in Jackalope.

"""


class _Phrase(object):

    @property
    def registration_confirmation(self):
        return "You're registered!"

    @property
    def task_posted_note(self):
        return "We posted the task to TaskRabbit."

    @property
    def task_completed_note(self):
        return "Your task has been completed. Way to get it done."

Phrase = _Phrase()
