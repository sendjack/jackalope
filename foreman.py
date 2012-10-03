""" Module: foreman

This module handles all coordination between Employer and Employee workers.

"""
from worker.asana_employer import AsanaEmployer
from worker.task_rabbit_employee import TaskRabbitEmployee

from job import Job


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
        tr = self._employees[0]

        employer_tasks = {}
        for employer in self._employers:
            employer_tasks = employer.read_tasks()

            # process each Task and either create or fetch its complement
            for employer_task in employer_tasks.values():
                employer_task._print_task() if employer_task else None

                employee_task = None

                # if task has a complement, go get it, else create it.
                reciprocal_id = employer_task.reciprocal_id
                if reciprocal_id:
                    employee_task = tr.read_task(reciprocal_id)
                    print employee_task.name
                else:
                    employee_task = tr.create_task(employer_task)
                    print "TASK CREATED: {}".format(employee_task)

                # hand the Tasks over to a Job and evaluate the statuses.
                job = Job(employer_task, employee_task)
                job.process(employer, tr)
