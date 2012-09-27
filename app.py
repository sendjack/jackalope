#!/usr/bin/env python
""" Module: app

Jackalope Test to mess around with connecting the Asana API to the TaskRabbit
API.

"""
from foreman import Foreman
#from worker.task_rabbit_employee import TaskRabbitEmployee


def main():
    foreman = Foreman()
    foreman.send_jack()


    #employee = TaskRabbitEmployee()
    #task = employee.read_task(54)
    #print task.name

    #print "NOW TO CREATION"
    #tr_response = employee.create_task(tasks.values()[0])
    #print tr_response


if __name__ == "__main__":
    main()
