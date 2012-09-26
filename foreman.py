""" Module: foreman

This module handles all coordination between Employer and Employee workers.

"""
from util.decorators import constant
from worker.asana_employer import AsanaEmployer
from worker.task_rabbit_employee import TaskRabbitEmployee


class _Status(object):

    """ Task Status Constants. """

    @constant
    def NEW_TASK(self):
        return "new_task"

    @constant
    def SPECIFICATION_INCOMPLETE(self):
        return "specification_incomplete"

    @constant
    def SPECIFICATION_COMPLETE(self):
        return "specification_complete"

    @constant
    def SUBMITTED_TO_EMPLOYEE(self):
        return "submitted_to_employee"

    @constant
    def ASSIGNED_TO_EMPLOYEE(self):
        return "assigned_to_employee"

    @constant
    def WORK_COMPLETE(self):
        return "work_complete"

    @constant
    def TASK_COMPLETE(self):
        return "task_complete"

STATUS = _Status()


class Foreman(object):

    """ Manage all Employer, Employee, Task interactions.

    Required:
    list employers      a list of all Employers to poll.
    list employees      a list of all Employees to push to.

    """


    def __init__(self):
        """ Construct a Foreman. """
        self._employers = [
                AsanaEmployer()
                ]

        self._employees = [
                TaskRabbitEmployee()
                ]


    def send_jack(self):
        """ Poll workers for Tasks and respond to them. """
        tasks = {}
        for e in self._employers:
            # TODO: prune tasks already completed
            tasks = e.read_tasks()

            self._print_tasks(tasks)

            # FIXME: All of this might happen in the worker?

            for id, task in tasks.items():
                status = self._evaluate_task(task)

                if status == STATUS.SPECIFICATION_INCOMPLETE:
                    e.request_fields(task)
                    print "spec incomplete"
                elif status == STATUS.SPECIFICATION_COMPLETE:
                    e.finish_task(task)
                    print "spec complete"
                else:
                    print "ERROR: We don't handle other cases yet."


        tr = self._employees[0]

        task = tr.read_task(54)
        print task.name

        print "NOW TO CREATION"
        tr_response = tr.create_task(tasks.values()[0])
        print tr_response


    def _evaluate_task(self, task):
        """ Evaluate the status of the task.

        Required:
        Task task   the task to evaluate.

        Return: STATUS

        """
        if task.is_spec_complete():
            return STATUS.SPECIFICATION_COMPLETE
        else:
            return STATUS.SPECIFICATION_INCOMPLETE


    def _print_tasks(self, tasks):
        """ Print all tasks. """
        print "\nTASKS\n--------"
        for t in tasks.values():
            print "id:", t.id
            print "name:", t.name
            print "price:", t.price
            print "email:", t.email
            print "description:", t.description
            print "spec complete?:", t.is_spec_complete()
            print ""
