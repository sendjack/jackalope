""" Module: foreman

This module handles all coordination between Employer and Employee workers.

"""
import settings
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


    def get_task_rabbit_worker(self):
        """ Return an instance of the TaskRabbitEmployee. """
        return self._employees[0]


    def get_asana_worker(self):
        """ Return an instance of the AsanaEmployer. """
        return self._employers[0]


    def send_jack(self):
        """ Poll workers for Tasks and respond to them. """
        employer_tasks = {}
        for employer in self._employers:
            employer_tasks = employer.read_tasks()
            self.process_employer_tasks(employer, employer_tasks)


    def process_employer_tasks(self, employer, tasks):
        """ Process employer Tasks by creating a Job for each Task and
        processing it.

        Required:
        Employer employer   The Employer whose tasks to process
        dict tasks          The Tasks to process.

        """
        for task in tasks.values():
            if task:
                print ""
                print task.id
                # hand the Tasks over to a Job and evaluate the statuses.
                # keep on processing Task until it doesn't change.
                task_to_process = task
                while task_to_process:
                    task_to_process._print_task()
                    job = JobFactory.instantiate_job_from_employer(
                            employer,
                            task_to_process,
                            self)
                    task_to_process = job.process()


    def process_employee_tasks(self, employee, tasks):
        """ Process employee Tasks by creating a Job for each Task and
        processing it.

        Required:
        dict tasks  The Tasks to process.

        """
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)
