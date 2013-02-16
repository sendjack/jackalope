"""
    phrase
    ------

    The special Jackalope language that brings Jack to life.

"""

from jutil.decorators import constant


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
        return unicode("A New Comment")

    @property
    def registration_confirmation(self):
        return unicode("You're registered!")

    @property
    def task_posted_note(self):
        return unicode("We posted the task to TaskRabbit.")

    @property
    def task_assigned_note(self):
        return unicode(
                "Your task is being worked on by a real live Jackalope.")

    @property
    def task_completed_note(self):
        return unicode("Your task has been completed. Way to get it done.")

    @property
    def task_approved_note(self):
        return unicode(
                "You approved your task. Hope you enjoyed using Jackalope.")

    @property
    def jackalope_intro(self):
        return unicode(
                "This task was posted to TaskRabbit by a third party service "
                "called Jackalope. Jackalope is the easiest way for small "
                "businesses to get their work done. To learn more, visit "
                "http://sendjack.com. \n\nIn order for you to communicate "
                "directly with the person who posted this task, we've created "
                "a unique email address just for the two of you. This should "
                "help things go more smoothly.\n\nInstead of using the email "
                "TaskRabbit lists for Jack, the task poster, please send all "
                "task-related email to:\n\n"
                )

Phrase = _Phrase()
