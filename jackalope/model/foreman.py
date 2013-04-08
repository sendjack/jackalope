"""
    foreman
    -------

    Handle all coordination between Employer and Employee workers.

"""

from worker.asana_employer import AsanaEmployer, ASANA
from worker.send_jack_employer import SendJackEmployer, SEND_JACK
from worker.task_rabbit_employee import TaskRabbitEmployee, TASK_RABBIT

from .data.db_worker import DbWorker
from .workflow import WorkflowFactory


class Foreman(object):

    """Manage all Employer, Employee, Task interactions.

    Attributes
    ----------
    _employers : dict
    _employees : dict
    _workers : dict

    """


    def __init__(self):
        self._employers = {
                ASANA.VENDOR: AsanaEmployer(),
                SEND_JACK.VENDOR: SendJackEmployer()
                }

        self._employees = {
                TASK_RABBIT.VENDOR: TaskRabbitEmployee()
                }

        self._workers = {}
        self._workers.update(self._employers)
        self._workers.update(self._employees)


    def get_worker(self, key=None):
        """Return the requested worker, but if no worker requested, then return
        the default employee, TaskRabbit."""
        return self._workers.get(key, self._employees.get(TASK_RABBIT.VENDOR))


    def ferry_comment(self, sender_vendor, sender_vendor_task_id, message):
        """Add the comment to the reciprocal task."""

        # look up the corresponding vendor and vendor_task_id
        db_worker = DbWorker()
        (recipient_vendor_task_id, recipient_vendor_name) = (
                db_worker.get_reciprocal_task_info(
                    sender_vendor_task_id,
                    sender_vendor))
        recipient_worker = self._workers.get(recipient_vendor_name)

        # send out the comment to the recipient
        new_comment = recipient_worker.add_comment(
                recipient_vendor_task_id,
                message)

        return new_comment is not None


    def send_jack(self):
        """Process all Jackalope services and handle `Task` updates."""
        employer_tasks = {}
        for employer in self._employers:
            employer_tasks = employer.read_tasks()
            # employer_tasks[id] = None when the task is not spec ready
            self._process_employer_tasks(employer, employer_tasks)


    def send_jack_for_task(self, vendor_name, task_id):
        employer = self._employers.get(vendor_name)
        if employer:
            employer_tasks = {task_id: employer.read_task(task_id)}
            self._process_employer_tasks(employer, employer_tasks)
        else:
            employee = self._employees.get(vendor_name)
            employee_tasks = {task_id: employee.read_task(task_id)}
            self._process_employee_tasks(employee, employee_tasks)


    def _process_employer_tasks(self, employer, tasks):
        """Process a dict of `Employer` service `Task` keyed on id."""
        print "\n STEP: PROCESS THE EMPLOYER TASKS ------>\n"

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
        print "\n STEP: PROCESS THE EMPLOYEE TASKS ------>\n"

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

                    workflow = WorkflowFactory.instantiate_from_employee(
                            employee,
                            task_to_process,
                            self)
                    task_to_process = workflow.process()

                    process_iterations = process_iterations + 1

                print "END proccessing task", id, "\n"
