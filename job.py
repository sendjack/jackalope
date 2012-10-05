""" Module: job

Job is a combination of Tasks (currently a pair) that represents the total
state between services. The Foreman uses the Job to evaluate and process the
Employer's and Employee's Tasks.

This separation between Foreman and Job allows for more complicated Task
combinations in the future.

"""
import settings
from task import Task, PricedTask, RegistrationTask


class Job(object):

    """ A combination of Tasks.

    Required:
    Employer _employer       The Employer.
    Employee _employee       The Employee.
    Task _employer_task     The Employer half of the package.

    """


    def __init__(self, employer, employee, employer_task):
        """ Construct a Job.

        Required:
        Employer employer       The Employer.
        Employee employee       The Employee.
        Task employer_task      The Employer half of the package.

        """
        self._employer = employer
        self._employee = employee
        self._employer_task = employer_task


    def process(self):
        """ Evaluate the tasks and then use the Workers to process the
        Tasks. """
        raise NotImplementedError(settings.NOT_IMPLEMENTED_ERROR)


class SoloJob(Job):

    """ Evaluate a task from an Employer and take appropriate action but only
    on Tasks that won't have a paired Employee Task. """


    def process(self):
        """ Evaluate the tasks and then use the Workers to process the
        Tasks. """
        if self._employer_task.is_posted():
            self._employer.finish_task(self._employer_task)
            print "spec complete and taskrabbit task exists"


class PairedJob(Job):

    """ Evaluate the tasks and then use the Workers to process the Tasks. There
    will be one Employer and one Employee Task.

    Task _employee_task     The Employee half of the package.

    """


    def __init__(self, employer, employee, employer_task):
        """ Construct a Job.

        Required:
        Employer employer       The Employer.
        Employee Employee       The Employee.
        Task employer_task      The Employer half of the package.

        """
        super(PairedJob, self).__init__(employer, employee, employer_task)
        self._employee_task = self._read_or_create_employee_task(employer_task)


    def process(self):
        """ Evaluate the tasks and then use the Workers to process the
        Tasks. """
        # check to see if Status is in sync and act.
        if self._are_same_states(self._employer_task, self._employee_task):
            # both states are the same. do nothing.
            print "both states are the same."
        elif self._employee_task.is_assigned():
            # employee task is assigned. update employer task.
            print "update employer task to assigned."
        elif self._employee_task.is_completed():
            # employee task is completed. update employer task.
            print "update employer task to completed."
        elif self._employer_task.is_approved():
            # employer task is approved. update employee task.
            print "update employee task to appoved"
        else:
            # error state.
            # TODO: Throw error
            print "ERROR IN STATE COMPARISON."

        # check to see if Content is in sync and act.


    def _read_or_create_employee_task(self, employer_task):
        """ If the employee task exists then grab it, otherwise create it.

        Required:
        Task employer_task  The Task to use as starter.

        Return: Complementary Task

        """
        employee_task = None
        reciprocal_id = employer_task.reciprocal_id
        if reciprocal_id:
            employee_task = self._employee.read_task(reciprocal_id)
            print employee_task.name
        else:
            employee_task = self._employee.create_task(employer_task)
            print "TASK CREATED: {}".format(employee_task)

        return employee_task


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
    def instantiate_job(class_, employer, employee, employer_task):
        """ Use the Task's Class to constructa Job.

        Required:
        Employer employer       The Employer.
        Employee employee       The Employee.
        Task employer_task      The Employer half of the package.

        """
        task_class = type(employer_task)
        job_constructor = class_.JOB_TASK_MAPPING.get(task_class)

        print "EVAN"
        print task_class
        print job_constructor
        return job_constructor(employer, employee, employer_task)


class JobError(Exception):

    """ A generic error thrown by a Job if the workflow is not being respected.
    """

    def __init__(self):
        """ Construct a JobError. """
        self.reason = "JobError: You're using this Job incorrectly."
