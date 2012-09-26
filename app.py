#!/usr/bin/env python
""" Module: app

Jackalope Test to mess around with connecting the Asana API to the TaskRabbit
API.

"""
from foreman import Foreman


def main():
    foreman = Foreman()
    foreman.send_jack()


if __name__ == "__main__":
    main()
