#!/usr/bin/env python2
"""
TODO
"""
from __future__ import print_function

import getpass
import importlib
import json
import logging
import sys

from weboob.core import Weboob

from tools.jsonwriter import pretty_json

# Dynamically load capabilities conversion modules
CAPABILITIES_CONVERSION_MODULES = importlib.import_module("capabilities")


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
    logging.info("Start fetching from konnectors.")
    for module in used_modules:
        logging.info("Fetching data from module %s.", module["id"])
        # Get associated backend for this module
        backend = WeboobProxy(
            module["name"],
            module["parameters"]
        ).get_backend()
        # List all supported capabilities
        for capability in backend.iter_caps():
            # Convert capability class to string name
            capability = capability.__name__
            try:
                # Get conversion function for this capability
                fetching_function = (
                    getattr(
                        getattr(
                            CAPABILITIES_CONVERSION_MODULES,
                            capability
                        ),
                        "to_cozy"
                    )
                )
                logging.info("Fetching capability %s.", capability)
                # Fetch data and store them
                # TODO: Ensure there is no overwrite
                fetched_data[module["id"]] = fetching_function(backend)
            except AttributeError:
                logging.error("%s capability is not implemented.", capability)
                continue
    logging.info("Done fetching from konnectors.")
    return fetched_data


if __name__ == '__main__':
    try:
        logging.basicConfig(
            format='%(levelname)s: %(message)s',
            level=logging.INFO
        )
        try:
            konnectors = json.load(sys.stdin)
            # Handle missing passwords using getpass
            for module in range(len(konnectors)):
                for param in konnectors[module]["parameters"]:
                    if not konnectors[module]["parameters"][param]:
                        konnectors[module]["parameters"][param] = getpass.getpass(
                            "Password for module %s? " % konnectors[module]["id"]
                        )
        except ValueError:
            logging.error("Invalid JSON input.")
            sys.exit(-1)

        print(
            pretty_json(
                main(konnectors)
            )
        )
    except KeyboardInterrupt:
        pass
