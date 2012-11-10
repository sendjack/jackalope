"""
    phrase
    ------

    The special Jackalope language that brings Jack to life.

"""

from jackalope.util.decorators import constant


class _Name(object):

    @constant
    def PRODUCTION(self):
        return "Jack A. Lope"

    @constant
    def STAGING(self):
        return "Jack Staging"

    @constant
    def DEV(self):
        return "Jack Dev"

NAME = _Name()


class _Phrase(object):

    @property
    def new_comment_subject(self):
        return "A New Comment"

    @property
    def registration_confirmation(self):
        return "You're registered!"

    @property
    def task_posted_note(self):
        return "We posted the task to TaskRabbit."

    @property
    def task_assigned_note(self):
        return "Your task is being worked on by a real live Jackalope."

    @property
    def task_completed_note(self):
        return "Your task has been completed. Way to get it done."

    @property
    def task_approved_note(self):
        return "You approved your task. Hope you enjoyed using Jackalope."

    @property
    def jackalope_intro(self):
        return ("This task has been sent to you by a service called "
                "Jackalope. Jackalope pulls tasks from a number of sources. "
                "Please check us out at http://sendjack.com. \n\nMost "
                "importantly, we'd like to be able to communicate with the "
                "person who created this task, so we've created a unique "
                "email address to reach him or her. Please send all task "
                "related email to:"
                )

Phrase = _Phrase()
