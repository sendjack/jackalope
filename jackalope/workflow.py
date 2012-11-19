"""
    workflow
    --------

    Workflow manages the workflow to respond to task changes and synching
    between services. Foreman uses the Workflow to evaluate and process
    Employer and Employee Tasks.

    This separation between Foreman and Workflow allows for more complicated
    Task combinations in the future.

"""

from time import time

from jackalope.errors import OverrideRequiredError
from jackalope.phrase import Phrase
from jackalope.data.db_worker import DbWorker
from jackalope.task import Task, PricedTask, RegistrationTask


class Workflow(object):

    """Manage the workflow between services and Jackalope.

    Attributes
    ----------
    _worker : `ServiceWorker`
    _task : `Task`
    _forman : `Foreman`
    _is_employer_workflow: `bool`
        If Employer initiated this Workflow, then True.
    _task_changed : `bool`
        If the Task has been updated by this Workflow, then True.

    """


    def __init__(self, worker, task, foreman, is_employer_workflow=True):
        self._db_worker = DbWorker()
        self._worker = worker
        self._task = task
        self._foreman = foreman
        self._is_employer_workflow = is_employer_workflow
        self._task_changed = False

        # a Task must have a status before it gets handed to a Workflow.
        if not self._task.has_status():
            raise WorkflowError()


    def process(self):
        """Evaluate the tasks and then use the Workers to process the Tasks,
        returning a Task if it's been updated or None if it hasn't."""
        print "WORKFLOW: PROCESS"
        self._jack_task = self._fetch_jack_task(self._task.id(), )
        if self._jack_task is None:
            self._jack_task = self._task
            print "DB-TASK-TODO: create - write task to db"
        self._reconcile_state()


    def _fetch_jack_task(self, task_id):
        """Fetch Jackalope version of Task from the DB and return it."""
        print "DB-TASK-TODO: read - read task from db"
        return None

    def _reconcile_state(self):
        """Evaluate the Tasks, update them appropriately, and return a Task if
        it's been updated or None if it hasn't."""
        raise OverrideRequiredError()


class SoloWorkflow(Workflow):

    """Evaluate a Task from an Employer but only handle workflows where there
    is not an additional service or Task."""

    def _reconcile_state(self):
        """Evaluate the Tasks, update them appropriately, and return a Task if
        it's been updated or None if it hasn't."""
        # only process SoloWorkflows from Employers.
        if not self._is_employer_workflow:
            raise WorkflowError()

        # if posted, then complete.
        if self._task.is_posted():
            print "DB-TASK-TODO: update - update jack task to completed"
            self._task = self._worker.update_task_to_completed(self._task)
            self._worker.add_comment(
                    self._task.id(),
                    Phrase.registration_confirmation)
            self._task_changed = True
        # if completed, then do nothing.
        elif self._task.is_completed():
            self._task_changed = False
        # any other case is an error.
        else:
            raise WorkflowError()

        updated_task = None
        if self._task_changed:
            updated_task = self._task
        return updated_task


class PairedWorkflow(Workflow):

    """Evaluate the Tasks and then use the Workers to handle any updates or
    synching that needs to occur between the services.

    Attributes
    ----------
    _reciprocal_worker : `ServiceWorker`
    _reciprocal_task : `Task`
    _reciprocal_task_changed : `bool`

    """


    def __init__(self, worker, task, foreman, is_employer_workflow=True):
        super(PairedWorkflow, self).__init__(
                worker,
                task,
                foreman,
                is_employer_workflow)

        self._reciprocal_task_changed = False
        self._set_smart_reciprocal_worker()
        self._set_reciprocal_task()


    def _reconcile_state(self):
        """Evaluate the Tasks, update them appropriately, and return a Task if
        it's been updated or None if it hasn't."""
        # check to see if Status is in sync and act.
        # both states are the same. do nothing.
        if self._are_same_states(
                self._get_employer_task(),
                self._get_employee_task()):
            print "same state"
        # employee task is assigned and employer task is posted, then update
        elif (
                self._get_employee_task().is_assigned() and
                self._get_employer_task().is_posted()
                ):
            print "assigned update"
            print "DB-TASK-TODO: update - update jack task to assigned"
            updated_task = self._get_employer().update_task_to_assigned(
                    self._get_employer_task())
            self._update_employer_task(updated_task)
        # employee task is completed and employer task is assigned, then update
        elif (
                self._get_employee_task().is_completed() and
                self._get_employer_task().is_assigned() or
                self._get_employer_task().is_posted()
                ):
            print "completed update"
            print "DB-TASK-TODO: update - update jack task to completed"
            updated_task = self._get_employer().update_task_to_completed(
                    self._get_employer_task())
            self._update_employer_task(updated_task)
        # employer task is approved. update employee task.
        elif self._get_employer_task().is_approved():
            print "approved update"
            print "DB-TASK-TODO: update - update jack task to approced"
            updated_task = self._get_employee().update_task_to_approved(
                    self._get_employee_task())
            self._update_employee_task(updated_task)
        # error state.
        else:
            raise WorkflowError()

        # check to see if Content is in sync and act.

        # sync comments between the services when they've been paired
        # FIXME: Currently only pulls comments from workflow initiator
        # (employer)
        if (
                self._task.is_assigned() or
                self._task.is_completed() or
                self._task.is_approved()):
            comments = self._worker.read_comments(self._task.id())
            self._task.set_comments(comments)
            synched_ts = self._db_worker.get_synched_ts(
                    self._task.id(),
                    self._worker.name())
            new_comments = self._task.get_comments_since_ts(synched_ts)
            if new_comments:
                self._task_changed = True
            for comment in new_comments:
                self._reciprocal_worker.add_comment(
                        self._reciprocal_task.id(),
                        comment.message())

        # if either task has changed make sure synch ts is updated and pushed.
        updated_task = None
        current_ts = int(time())
        if self._task_changed:
            self._db_worker.update_vendor_synched_ts(
                    self._task.id(),
                    self._worker.name(),
                    current_ts)
            updated_task = self._worker.update_task(self._task)
        if self._reciprocal_task_changed:
            self._db_worker.update_vendor_synched_ts(
                    self._reciprocal_task.id(),
                    self._reciprocal_worker.name(),
                    current_ts)
            # TODO: uncomment this line when TaskRabbitWorker.update_task works
            #self._reciprocal_worker.update_task(self._reciprocal_task)
        return updated_task


    def _get_employer(self):
        # this conditional allows the Workflow to be initiated by an Employee
        # or Employer
        employer = None
        if self._is_employer_workflow:
            employer = self._worker
        else:
            employer = self._reciprocal_worker
        return employer


    def _get_employee(self):
        # this conditional allows the Workflow to be initiated by an Employee
        # or Employer
        employee = None
        if self._is_employer_workflow:
            employee = self._reciprocal_worker
        else:
            employee = self._worker
        return employee


    def _get_employer_task(self):
        # this conditional allows the Workflow to be initiated by an Employee
        # or Employer
        employer_task = None
        if self._is_employer_workflow:
            employer_task = self._task
        else:
            employer_task = self._reciprocal_task
        return employer_task


    def _update_employer_task(self, updated_task):
        # this conditional allows the Workflow to be initiated by an Employee
        # or Employer
        if self._is_employer_workflow:
            self._task = updated_task
            self._task_changed = True
        else:
            self._reciprocal_task = updated_task
            self._reciprocal_task_changed = True


    def _get_employee_task(self):
        # this conditional allows the Workflow to be initiated by an Employee
        # or Employer
        employee_task = None
        if self._is_employer_workflow:
            employee_task = self._reciprocal_task
        else:
            employee_task = self._task
        return employee_task


    def _update_employee_task(self, updated_task):
        # this conditional allows the Workflow to be initiated by an Employee
        # or Employer
        if self._is_employer_workflow:
            self._reciprocal_task = updated_task
            self._reciprocal_task_changed = True
        else:
            self._task = updated_task
            self._task_changed = True


    def _set_smart_reciprocal_worker(self):
        """Figure out which reciprocal ServiceWorker should match this Task and
        set the *_reciprocal_worker*."""
        # TODO make this function pull from a dictionary or database
        if self._is_employer_workflow:
            self._reciprocal_worker = self._foreman.get_task_rabbit_worker()
        else:
            self._reciprocal_worker = self._foreman.get_asana_worker()


    def _set_reciprocal_task(self):
        """Set the *_reciprocal_task* and create it first if it doesn't
        exist."""
        (reciprocal_id, reciprocal_service_name) = (
                self._db_worker.get_reciprocal_task_info(
                        self._task.id(),
                        self._worker.name()))
        # if it exists, just store it.
        if reciprocal_id:
            self._reciprocal_task = self._reciprocal_worker.read_task(
                    reciprocal_id)
        else:
            # if it doesn't exist and the Workflow was started by an employer,
            # then create it.
            if self._is_employer_workflow:
                self._reciprocal_task = self._create_reciprocal_task()
            # Employee initiated Workflows cannot create reciprocal tasks.
            else:
                raise WorkflowError()


    def _create_reciprocal_task(self):
        """Create a Task to be the recipricol of the Workflow's *_task*, link
        the two Tasks, and return the new one."""
        reciprocal_task = self._reciprocal_worker.create_task(self._task)
        self._db_worker.create_vendor_task(
                self._task.id(),
                self._worker.name(),
                0,
                reciprocal_task.id(),
                self._reciprocal_worker.name())

        self._db_worker.create_vendor_task(
                reciprocal_task.id(),
                self._reciprocal_worker.name(),
                0,
                self._task.id(),
                self._worker.name())

        self._task = self._worker.update_task(self._task)
        #self._worker.add_comment(
        #        self._task.id(),
        #        Phrase.task_posted_note)
        self._task_changed = True

        return reciprocal_task


    @staticmethod
    def _are_same_states(task1, task2):
        """If both Tasks have the same status, then return True."""
        are_same_states = False

        if task1.is_posted() and task2.is_posted():
            are_same_states = True
        elif task1.is_assigned() and task2.is_assigned():
            are_same_states = True
        elif task1.is_completed() and task2.is_completed():
            are_same_states = True
        elif task1.is_approved() and task2.is_approved():
            are_same_states = True

        return are_same_states


class WorkflowFactory(object):

    """Construct a Workflow with the subclass depending on the subclass of
    Task."""

    # Use the Task Class to map to the correct Workflow.
    WORKFLOW_TASK_MAPPING = {
            Task: PairedWorkflow,
            RegistrationTask: SoloWorkflow,
            PricedTask: PairedWorkflow
            }


    @classmethod
    def instantiate_from_employer(
            class_,
            employer,
            employer_task,
            foreman):
        print "WORKFLOW: INSTANTIATE"
        task_class = type(employer_task)
        workflow_constructor = class_.WORKFLOW_TASK_MAPPING.get(task_class)
        workflow = workflow_constructor(employer, employer_task, foreman)

        return workflow


class WorkflowError(Exception):


    def __init__(self):
        self.reason = "WorkflowError: You're using this Workflow incorrectly."
