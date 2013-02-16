"""
    foreman
    -------

    Handle all coordination between Employer and Employee workers.

"""

from worker.asana_employer import AsanaEmployer
from worker.task_rabbit_employee import TaskRabbitEmployee

from workflow import WorkflowFactory


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


    def ferry_comment(self, service, from_task_id, message):
        """Add the comment to the reciprocal task."""
        new_comment = None

        if service == "taskrabbit":
            # when the reciprocal id is in the tr task
            # tr_worker = self.get_task_rabbit_worker()
            # from_task = tr_worker.read_task(from_task_id)
            # to_task_id = from_task.reciprocal_id()

            asana_worker = self.get_asana_worker()

            # FIXME: the 'from_task_id' is actually the to_task_id' because we
            # don't have the from_task_id when this is set.
            to_task_id = from_task_id
            # remove when reciprocal id comes from tr
            #tasks = asana_worker.read_tasks()
            #to_task_id = -1
            #for id, to_task in tasks.items():
            #    if to_task.reciprocal_id() == from_task_id:
            #        to_task_id = id

            new_comment = asana_worker.add_comment(
                    to_task_id,
                    message)
        else:
            print "only handling comments from taskrabbit"

        return new_comment is not None


    def send_jack(self):
        """Process all Jackalope services and handle `Task` updates."""
        employer_tasks = {}
        for employer in self._employers:
            employer_tasks = employer.read_tasks()
            # employer_tasks[id] = None when the task is not spec ready
            self._process_employer_tasks(employer, employer_tasks)


    def _process_employer_tasks(self, employer, tasks):
        """Process a dict of `Employer` service `Task` keyed on id."""
        print "\n STEP 2: PROCESS THE TASKS ------>\n"

        for task in tasks.values():
            if task is not None:
                # hand the Tasks over to a Workflow and evaluate the statuses.
                # keep on processing Task until it doesn't change.
                task_to_process = task
                id = task.id()
                process_iterations = 0
                print "START processing task", id

                while task_to_process:
                    task_to_process._print_task()
                    print "\t processed task", process_iterations, "times\n"

                    workflow = WorkflowFactory.instantiate_from_employer(
                            employer,
                            task_to_process,
                            self)
                    task_to_process = workflow.process()

                    process_iterations = process_iterations + 1

                print "END proccessing task", id, "\n"


    def _process_employee_tasks(self, employee, tasks):
        """Process a dict of `Employee` service `Task` keyed on id."""
        raise NotImplementedError()
