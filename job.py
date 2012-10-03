""" Module: job

Job is a combination of Tasks (currently a pair) that represents the total
state between services. The Foreman uses the Job to evaluate and process the
Employer's and Employee's Tasks.

This separation between Foreman and Job allows for more complicated Task
combinations in the future.

"""


class Job(object):

    """ A combination of Tasks.

    Required:
    Task _employer_task     The Employer half of the package.
    Task _employee_task     The Employee half of the package.

    """


    def __init__(self, employer_task, employee_task):
        """ Construct a Job.

        Required:
        Task employer_task     The Employer half of the package.
        Task employee_task     The Employee half of the package.

        """
        self._employer_task = employer_task
        self._employee_task = employee_task


    def process(self, employer_worker, employee_worker):
        """ Evaluate the tasks and then use the Workers to process the Tasks.

        Required:
        ServiceWorker employer_worker       The Employer.
        ServiceWorker employee_worker       The Employee.

        """
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

        # FIXME XXX: figure out what to do about our solo registration task.
        # if status == STATUS.POSTED:
        #    employer_task.worker.finish_task(employer_task)
        #    print "spec complete and taskrabbit task exists"


    @staticmethod
    def _are_same_states(task1, task2):
        """ Return True if both tasks are in the same state. """
        are_same_states = False

        if task1.is_posted and task2.is_posted:
            are_same_states = True
        elif task1.is_assigned and task2.is_assigned:
            are_same_states = True
        elif task1.is_completed and task2.is_completed:
            are_same_states = True
        elif task1.is_approved and task2.is_approved:
            are_same_states = True

        return are_same_states
