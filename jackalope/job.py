"""
    job
    ---

    Job manages the workflow to respond to task changes and synching between
    services. Foreman uses the Job to evaluate and process Employer and
    Employee Tasks.

    This separation between Foreman and Job allows for more complicated Task
    combinations in the future.

"""

from jackalope import settings
from jackalope.phrase import Phrase
from jackalope.task import Task, PricedTask, RegistrationTask


class Job(object):

    """Manage the workflow between services and Jackalope.

    Attributes
    ----------
    _worker : `ServiceWorker`
    _task : `Task`
    _forman : `Foreman`
    _is_employer_job : `bool`
        If Employer initiated this Job, then True.
    _task_changed : `bool`
        If the Task has been updated by this Job, then True.

    """


    def __init__(self, worker, task, foreman, is_employer_job=True):
        self._worker = worker
        self._task = task
        self._foreman = foreman
        self._is_employer_job = is_employer_job
        self._task_changed = False

        # a Task must have a status before it gets handed to a Job.
        if not self._task.has_status():
            raise JobError()


    def process(self):
        """Evaluate the tasks and then use the Workers to process the Tasks,
        returning a Task if it's been updated or None if it hasn't."""
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)


class SoloJob(Job):

    """Evaluate a Task from an Employer but only handle workflows where there
    is not an additional service or Task."""

    def process(self):
        """Evaluate the tasks and then use the Workers to process the Tasks,
        returning a Task if it's been updated or None if it hasn't."""
        # only process SoloJobs from Employers.
        if not self._is_employer_job:
            raise JobError()

        print "getting here"

        # if posted, then complete.
        if self._task.is_posted():
            self._task = self._worker.update_task_to_completed(self._task)
            self._worker.add_comment(
                    self._task,
                    Phrase.registration_confirmation)
            self._task_changed = True
        # if completed, then do nothing.
        elif self._task.is_completed():
            self._task_changed = False
        # any other case is an error.
        else:
            raise JobError()

        updated_task = None
        if self._task_changed:
            updated_task = self._task
        return updated_task


class PairedJob(Job):

    """Evaluate the Tasks and then use the Workers to handle any updates or
    synching that needs to occur between the services.

    Attributes
    ----------
    _reciprocal_worker : `ServiceWorker`
    _reciprocal_task : `Task`
    _reciprocal_task_changed : `bool`

    """


    def __init__(self, worker, task, foreman, is_employer_job=True):
        super(PairedJob, self).__init__(worker, task, foreman, is_employer_job)

        self._reciprocal_task_changed = False
        self._set_smart_reciprocal_worker()
        self._set_reciprocal_task()


    def process(self):
        """Evaluate the tasks and then use the Workers to process the Tasks,
        returning a Task if it's been updated or None if it hasn't."""
        print "PROCESS THE JOB"
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
            updated_task = self._get_employer().update_task_to_assigned(
                    self._get_employer_task())
            self._update_employer_task(updated_task)
        # employee task is completed and employer task is assigned, then update
        elif (
                self._get_employee_task().is_completed() and
                self._get_employer_task().is_assigned()
                ):
            print "completed update"
            updated_task = self._get_employer().update_task_to_completed(
                    self._get_employer_task())
            self._update_employer_task(updated_task)
        # employer task is approved. update employee task.
        elif self._get_employer_task().is_approved():
            print "approved update"
            updated_task = self._get_employee().update_task_to_approved(
                    self._get_employee_task())
            self._update_employee_task(updated_task)
        # error state.
        else:
            raise JobError()

        # check to see if Content is in sync and act.

        # if either task has changed make sure synch ts is updated and pushed.
        updated_task = None
        if self._task_changed:
            self._task.push_current_to_last_synched()
            updated_task = self._worker.update_task(self._task)
        if self._reciprocal_task_changed:
            self._reciprocal_task.push_current_to_last_synched()
            # TODO: uncomment this line when TaskRabbitWorker.update_task works
            #self._reciprocal_worker.update_task(self._reciprocal_task)
        return updated_task


    def _get_employer(self):
        # this conditional allows the Job to be initiated by an Employee or
        # Employer
        employer = None
        if self._is_employer_job:
            employer = self._worker
        else:
            employer = self._reciprocal_worker
        return employer


    def _get_employee(self):
        # this conditional allows the Job to be initiated by an Employee or
        # Employer
        employee = None
        if self._is_employer_job:
            employee = self._reciprocal_worker
        else:
            employee = self._worker
        return employee


    def _get_employer_task(self):
        # this conditional allows the Job to be initiated by an Employee or
        # Employer
        employer_task = None
        if self._is_employer_job:
            employer_task = self._task
        else:
            employer_task = self._reciprocal_task
        return employer_task


    def _update_employer_task(self, updated_task):
        # this conditional allows the Job to be initiated by an Employee or
        # Employer
        if self._is_employer_job:
            self._task = updated_task
            self._task_changed = True
        else:
            self._reciprocal_task = updated_task
            self._reciprocal_task_changed = True


    def _get_employee_task(self):
        # this conditional allows the Job to be initiated by an Employee or
        # Employer
        employee_task = None
        if self._is_employer_job:
            employee_task = self._reciprocal_task
        else:
            employee_task = self._task
        return employee_task


    def _update_employee_task(self, updated_task):
        # this conditional allows the Job to be initiated by an Employee or
        # Employer
        if self._is_employer_job:
            self._reciprocal_task = updated_task
            self._reciprocal_task_changed = True
        else:
            self._task = updated_task
            self._task_changed = True


    def _set_smart_reciprocal_worker(self):
        """Figure out which reciprocal ServiceWorker should match this Task and
        set the *_reciprocal_worker*."""
        # TODO make this function pull from a dictionary or database
        if self._is_employer_job:
            self._reciprocal_worker = self._foreman.get_task_rabbit_worker()
        else:
            self._reciprocal_worker = self._foreman.get_asana_worker()


    def _set_reciprocal_task(self):
        """Set the *_reciprocal_task* and create it first if it doesn't
        exist."""
        reciprocal_id = self._task.reciprocal_id()
        # if it exists, just store it.
        if reciprocal_id:
            self._reciprocal_task = self._reciprocal_worker.read_task(
                    reciprocal_id)
        else:
            # if it doesn't exist and the Job was started by an employer, then
            # create it.
            if self._is_employer_job:
                self._reciprocal_task = self._create_reciprocal_task()
            # Employee initiated Jobs cannot create reciprocal tasks.
            else:
                raise JobError()


    def _create_reciprocal_task(self):
        """Create a Task to be the recipricol of the Job's *_task*, link the
        two Tasks, and return the new one."""
        reciprocal_task = self._reciprocal_worker.create_task(self._task)
        self._task.set_reciprocal_id(reciprocal_task.id())
        self._task = self._worker.update_task(self._task)
        #self._worker.add_comment(
        #        self._task,
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


class JobFactory(object):

    """Construct a Job with the subclass depending on the subclass of Task."""

    # Use the Task Class to map to the correct Job.
    JOB_TASK_MAPPING = {
            Task: PairedJob,
            RegistrationTask: SoloJob,
            PricedTask: PairedJob
            }


    @classmethod
    def instantiate_job_from_employer(
            class_,
            employer,
            employer_task,
            foreman):
        print "jobfactory instantiating..."
        task_class = type(employer_task)
        job_constructor = class_.JOB_TASK_MAPPING.get(task_class)
        job = job_constructor(employer, employer_task, foreman)

        return job


class JobError(Exception):


    def __init__(self):
        self.reason = "JobError: You're using this Job incorrectly."
