#!/usr/bin/env python
""" Module: app

Jackalope Test to mess around with connecting the Asana API to the TaskRabbit
API.

"""
from foreman.asana_foreman import AsanaForeman


def main():
    foreman = AsanaForeman()
    specs = foreman.get_specs()

    for s in specs.values():
        print "id: {}".format(s.id)
        print "name: {}".format(s.name)
        print "price: {}".format(s.price)
        print "description: {}".format(s.description)
        print "ready?: {}".format(s.is_spec_ready())
        print ""


if __name__ == "__main__":
    print "start"
    main()
