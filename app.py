#!/usr/bin/env python
""" Module: app

Jackalope Test to mess around with connecting the Asana API to the TaskRabbit
API.

"""
from worker.asana_employer import AsanaEmployer
from worker.task_rabbit_employee import TaskRabbitEmployee


def main():
    employer = AsanaEmployer()
    tasks = employer.read_tasks()

    for s in tasks.values():
        print "id: {}".format(s.id)
        print "name: {}".format(s.name)
        print "price: {}".format(s.price)
        print "description: {}".format(s.description)
        print "ready?: {}".format(s.is_task_ready())
        print ""

    employee = TaskRabbitEmployee()
    task = employee.read_task(54)
    print task.name

    print "NOW TO CREATION"
    tr_response = employee.create_task(tasks.values()[0])
    print tr_response


if __name__ == "__main__":
    print "start"
    main()
