"""
    foreman
    -------

    Handle all coordination between Employer and Employee workers.

"""

from worker.asana_employer import AsanaEmployer
from worker.task_rabbit_employee import TaskRabbitEmployee

from job import JobFactory


class Foreman(object):

    """Manage all Employer, Employee, Task interactions.

    Attributes
    ----------
    employers : list of `Employer`
    employees : list of `Employee`

    """


    def __init__(self):
        self._employers = [
                AsanaEmployer()
                ]

        self._employees = [
                TaskRabbitEmployee()
                ]


    def get_task_rabbit_worker(self):
        """Return an instance of the `TaskRabbitEmployee`."""
        return self._employees[0]


    def get_asana_worker(self):
        """Return an instance of the `AsanaEmployer`."""
        return self._employers[0]


    def send_jack(self):
        """Process all Jackalope services and handle `Task` updates."""
        employer_tasks = {}
        for employer in self._employers:
            employer_tasks = employer.read_tasks()
            self.process_employer_tasks(employer, employer_tasks)


    def process_employer_tasks(self, employer, tasks):
        """Process a dict of `Employer` service `Task` keyed on id."""
        for task in tasks.values():
            if task:
                print ""
                print task.id
                # hand the Tasks over to a Job and evaluate the statuses.
                # keep on processing Task until it doesn't change.
                task_to_process = task
                count = 0
                while task_to_process:
                    print "count:", count
                    task_to_process._print_task()
                    job = JobFactory.instantiate_job_from_employer(
                            employer,
                            task_to_process,
                            self)
                    task_to_process = job.process()

                    count = count + 1


    def process_employee_tasks(self, employee, tasks):
        """Process a dict of `Employee` service `Task` keyed on id."""
        raise NotImplementedError()
