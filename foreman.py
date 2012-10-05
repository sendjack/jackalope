""" Module: foreman

This module handles all coordination between Employer and Employee workers.

"""
from worker.asana_employer import AsanaEmployer
from worker.task_rabbit_employee import TaskRabbitEmployee

from job import JobFactory


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
        employee = self._employees[0]

        employer_tasks = {}
        for employer in self._employers:
            employer_tasks = employer.read_tasks()

            # process each Task and either create or fetch its complement
            for employer_task in employer_tasks.values():
                if employer_task:
                    employer_task._print_task()

                    # hand the Tasks over to a Job and evaluate the statuses.
                    job = JobFactory.instantiate_job(
                            employer,
                            employee,
                            employer_task)
                    job.process()
