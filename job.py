""" Module: job

Job is a combination of Tasks (currently a pair) that represents the total
state between services. The Foreman uses the Job to evaluate and process the
Employer's and Employee's Tasks.

This separation between Foreman and Job allows for more complicated Task
combinations in the future.

"""
import settings
from phrase import Phrase
from task import Task, PricedTask, RegistrationTask


class Job(object):

    """ A combination of Tasks.

    Required:
    ServiceWorker _worker   The Job's main Worker.
    Task _task              The Job's main Task.
    Foreman _foreman        The Foreman in charge of the Job.
    bool _is_employer_job   If True then an Employer Task initiated this Job.
    bool _task_changed      True if the task has been updated by the Job.

    """


    def __init__(self, worker, task, foreman, is_employer_job=True):
        """ Construct a Job.

        Required:
        SerivceWorker worker
        Task task
        Foreman foreman

        Optional:
        bool is_employer_job

        """
        self._worker = worker
        self._task = task
        self._foreman = foreman
        self._is_employer_job = is_employer_job
        self._task_changed = False


    def process(self):
        """ Evaluate the tasks and then use the Workers to process the
        Tasks.

        Return: bool indicating if the main Task was changed.

        """
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)


class SoloJob(Job):

    """ Evaluate a task from a Employer and take appropriate action but only
    on Tasks that won't have a paired Employee Task. """


    def process(self):
        """ Evaluate the tasks and then use the Workers to process the
        Tasks.

        Return: bool indicating if the main Task was changed.

        """
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

    """ Evaluate the tasks and then use the Workers to process the Tasks. There
    will be one Employer and one Employee Task.

    Required:
    ServiceWorker _reciprocal_worker
    Task _reciprocal_task

    """


    def __init__(self, worker, task, foreman, is_employer_job=True):
        """ Construct a Job.

        Required:
        ServiceWorker worker
        Task task
        Foreman foreman
        bool is_employer_job

        """
        super(PairedJob, self).__init__(worker, task, foreman, is_employer_job)
        self._set_smart_reciprocal_worker()
        self._set_reciprocal_task()


    def process(self):
        """ Evaluate the tasks and then use the Workers to process the
        Tasks.

        Return: bool indicating if the main Task was changed.

        """
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

        updated_task = None
        if self._task_changed:
            updated_task = self._task
        return updated_task


    def _get_employer(self):
        """ Return the Employer's worker. """
        employer = None
        if self._is_employer_job:
            employer = self._worker
        else:
            employer = self._reciprocal_worker
        return employer


    def _get_employee(self):
        """ Return the Employee's worker. """
        employee = None
        if self._is_employer_job:
            employee = self._reciprocal_worker
        else:
            employee = self._worker
        return employee


    def _get_employer_task(self):
        """ Return the Employer's Task. """
        employer_task = None
        if self._is_employer_job:
            employer_task = self._task
        else:
            employer_task = self._reciprocal_task
        return employer_task


    def _update_employer_task(self, updated_task):
        """ Set a new Employer Task. """
        if self._is_employer_job:
            self._task = updated_task
        else:
            self._reciprocal_task = updated_task
        self._task_changed = True


    def _get_employee_task(self):
        """ Return the Employee's Task. """
        employee_task = None
        if self._is_employer_job:
            employee_task = self._reciprocal_task
        else:
            employee_task = self._task
        return employee_task


    def _update_employee_task(self, updated_task):
        """ Set a new Employee Task. """
        if self._is_employer_job:
            self._reciprocal_task = updated_task
        else:
            self._task = updated_task
        self._task_changed = True


    def _set_smart_reciprocal_worker(self):
        """ Return the right Employer for an employee Task. """
        # TODO make this function pull from a dictionary or database
        if self._is_employer_job:
            self._reciprocal_worker = self._foreman.get_task_rabbit_worker()
        else:
            self._reciprocal_worker = self._foreman.get_asana_worker()


    def _set_reciprocal_task(self):
        """ Set the reciprocal task by fetching it or by creating it. """
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
        """ Create a reciprocal task and return it. """
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
        """ Return True if both tasks are in the same state. """
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

    """ Use the Type of Task to determine which Job to instantiate. """

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
        """ Use the Task's Class to constructa Job.

        Required:
        Employer employer
        Task employer_task      The Employer half of the package.
        Foreman foreman

        """
        print ""
        print "jobfactory instantiating..."
        task_class = type(employer_task)
        job_constructor = class_.JOB_TASK_MAPPING.get(task_class)
        job = job_constructor(employer, employer_task, foreman)

        return job


class JobError(Exception):

    """ A generic error thrown by a Job if the workflow is not being respected.
    """

    def __init__(self):
        """ Construct a JobError. """
        self.reason = "JobError: You're using this Job incorrectly."
