#!/usr/bin/env python
"""
    Jackalope application object.
    -----------------------------

    Jackalope connects the Asana and Task Rabbit APIs.

"""

from foreman import Foreman


def main():
    foreman = Foreman()
    foreman.send_jack()


if __name__ == "__main__":
    main()
