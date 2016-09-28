#!/usr/bin/env python2
from __future__ import print_function

import getpass

from weboob.core import Weboob

from capabilities import bill
from tools.jsonwriter import pretty_json


class Connector(object):
    """
    Connector is a tool that connects to common websites like bank website,
    phone operator website... and that grabs personal data from there.
    Credentials are required to make this operation.

    Technically, connectors are weboob backend wrappers.
    """

    @staticmethod
    def version():
        return Weboob.VERSION

    def update(self):
        return self.weboob.update()

    def __init__(self, modulename, parameters):
        """
        Create a Weboob handle and try to load the modules.
        """
        self.weboob = Weboob()

        # Careful: this is extracted from weboob's code.
        # Install the module if necessary and hide the progress.
        class DummyProgress:
            def progress(self, a, b):
                pass

        repositories = self.weboob.repositories
        minfo = repositories.get_module_info(modulename)
        if minfo is not None and not minfo.is_installed():
            repositories.install(minfo, progress=DummyProgress())

        # Calls the backend.
        self.backend = self.weboob.build_backend(modulename, parameters)


def main(email, password=None):
    """
    Main code
    """
    if password is None:
        # Ask for password if not provided
        password = getpass.getpass("Password? ")

    connector = Connector(
        "amazon",
        {
            "website": "www.amazon.fr",
            "email": email,
            "password": password
        }
    )
    return bill.to_cozy(connector.backend)


if __name__ == '__main__':
    print(
        pretty_json(
            main(raw_input("Email? "))
        )
    )
