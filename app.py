#!/usr/bin/env python
""" Module: app

Jackalope Test to mess around with connecting the Asana API to the TaskRabbit
API.

"""
from foreman.asana_foreman import AsanaForeman
from worker.task_rabbit_worker import TaskRabbitWorker


def main():
    foreman = AsanaForeman()
    specs = foreman.read_specs()

    for s in specs.values():
        print "id: {}".format(s.id)
        print "name: {}".format(s.name)
        print "price: {}".format(s.price)
        print "description: {}".format(s.description)
        print "ready?: {}".format(s.is_spec_ready())
        print ""

    worker = TaskRabbitWorker()
    spec = worker.read_spec(54)
    print spec.name

    print "NOW TO CREATION"
    tr_response = worker.create_spec(specs.values()[0])
    print tr_response


if __name__ == "__main__":
    print "start"
    main()
