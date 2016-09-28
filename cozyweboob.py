#!/usr/bin/env python2
from __future__ import print_function

import getpass
import json
import sys

from weboob.core import Weboob

from capabilities import bill
from tools.jsonwriter import pretty_json


class WeboobProxy(object):
    """
    Connector is a tool that connects to common websites like bank website,
    phone operator website... and that grabs personal data from there.
    Credentials are required to make this operation.

    Technically, connectors are weboob backend wrappers.
    """

    @staticmethod
    def version():
        """
        Return Weboob version.
        """
        return Weboob.VERSION

    @staticmethod
    def update():
        """
        Ensure modules are up to date.
        """
        return Weboob().update()

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

    def get_backend(self):
        """
        Get the built backend.
        """
        return self.backend


def main(used_modules):
    """
    Main code
    """
    # Update all available modules
    # TODO: WeboobProxy.update()

    # Fetch data for the specified modules
    fetched_data = {}
    for module, parameters in used_modules.items():
        # TODO
        fetched_data["bills"] = bill.to_cozy(
            WeboobProxy(
                module,
                parameters
            ).get_backend()
        )
    return fetched_data


if __name__ == '__main__':
    try:
        konnectors = json.load(sys.stdin)
    except ValueError:
        sys.exit("Invalid input")  # TODO

    print(
        pretty_json(
            main(konnectors)
        )
    )
