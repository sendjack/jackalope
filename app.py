#!/usr/bin/env python
""" Module: app

Jackalope Test to mess around with connecting the Asana API to the TaskRabbit
API.

"""
from foreman.asana_foreman import AsanaForeman


def main():
    foreman = AsanaForeman()
    tasks = foreman.get_tasks()

    for t in tasks.values():
        print "id: {}".format(t.id)
        print "name: {}".format(t.name)
        print "price: {}".format(t.price)
        print "description: {}".format(t.description)
        print "ready?: {}".format(t.is_task_ready())
        print ""


if __name__ == "__main__":
    print "start"
    main()
