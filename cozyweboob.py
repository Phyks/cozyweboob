#!/usr/bin/env python2
"""
Wrapper script around Weboob to be able to use it in combination with Cozy +
Konnectors easily.

Part of this code comes from [Kresus](https://github.com/bnjbvr/kresus/)
written by bnjbvr and released under MIT.
"""
from __future__ import print_function

import collections
import importlib
import json
import logging
import sys

from getpass import getpass

from requests.utils import dict_from_cookiejar
from weboob.core import Weboob

from tools.env import is_in_debug_mode
from tools.jsonwriter import pretty_json
from tools.progress import DummyProgress

# Dynamically load capabilities conversion modules
# Dynamic loading is required to be able to call them programatically.
CAPABILITIES_CONVERSION_MODULES = importlib.import_module("capabilities")

# Module specific logger
logger = logging.getLogger(__name__)


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
        Get Weboob version.

        Returns:
            the version of installed Weboob.
        """
        return Weboob.VERSION

    @staticmethod
    def update():
        """
        Ensure modules are up to date.
        """
        Weboob().update(progress=DummyProgress())

    def __init__(self):
        """
        Create a Weboob handle.
        """
        # Get a weboob instance
        self.weboob = Weboob()
        self.backend = None

    def install_modules(self, capability=None, name=None):
        """
        List all available modules and their configuration options.

        Args:
            capability: Restrict the modules to install to a given capability.
            name: Only install the specified module.
        Returns: The list of installed module infos.
        """
        repositories = self.weboob.repositories
        if name:
            modules = [repositories.get_module_info(name)]
        else:
            modules = repositories.get_all_modules_info(capability)
        for module in modules:
            if module is not None and not module.is_installed():
                repositories.install(module, progress=DummyProgress())
        return modules

    def init_backend(self, modulename, parameters):
        """
        Backend initialization.

        Returns:
            the built backend.
        """
        # Ensure module is installed
        self.install_modules(name=modulename)
        # Build backend
        self.backend = self.weboob.build_backend(modulename, parameters)
        return self.backend


def main_fetch(used_modules):
    """
    Main fetching code

    Args:
        used_modules: A list of modules description dicts.
    Returns: A dict of all the results, ready to be JSON serialized.
    """
    # Update all available modules
    logger.info("Update all available modules.")
    WeboobProxy.update()
    logger.info("Done updating available modules.")

    # Fetch data for the specified modules
    fetched_data = collections.defaultdict(dict)
    logger.info("Start fetching from konnectors.")
    for module in used_modules:
        try:
            weboob_proxy = WeboobProxy()
            logger.info("Fetching data from module %s.", module["id"])
            # Get associated backend for this module
            backend = weboob_proxy.init_backend(
                module["name"],
                module["parameters"]
            )
            for capability in backend.iter_caps():  # Supported capabilities
                # Get capability class name for dynamic import of converter
                capability = capability.__name__
                try:
                    fetching_function = (
                        getattr(
                            getattr(
                                CAPABILITIES_CONVERSION_MODULES,
                                capability
                            ),
                            "to_cozy"
                        )
                    )
                    logger.info("Fetching capability %s.", capability)
                    # Fetch data and merge them with the ones from other
                    # capabilities
                    fetched_data[module["id"]].update(
                        fetching_function(backend)
                    )
                except AttributeError:
                    # In case the converter does not exist on our side
                    logger.error("%s capability is not implemented.",
                                 capability)
                    continue
            # Store session cookie of this module, to fetch files afterwards
            try:
                fetched_data[module["id"]]["cookies"] = dict_from_cookiejar(
                    backend.browser.session.cookies
                )
            except AttributeError:
                # Avoid an AttributeError if no session is used for this module
                fetched_data[module["id"]]["cookies"] = None
        except Exception as e:
            # Store any error happening in a dedicated field
            fetched_data[module["id"]]["error"] = e
            if is_in_debug_mode():
                # Reraise if in debug
                raise
            else:
                # Skip any errored module when not in debug
                continue
    logger.info("Done fetching from konnectors.")
    return fetched_data


def main(json_params):
    """
    Main code

    Args:
        json_params: A JSON string representing the params to use.
    Returns: A JSON string of the results.
    """
    try:
        # Fetch konnectors JSON description from stdin
        konnectors = json.loads(json_params)
        # Debug only: Handle missing passwords using getpass
        if is_in_debug_mode():
            for module in konnectors:
                for param in module["parameters"]:
                    if not module["parameters"][param]:
                        module["parameters"][param] = getpass(
                            "Password for module %s? " % (
                                module["id"],
                            )
                        )
    except ValueError:
        logger.error("Invalid JSON input.")
        sys.exit(-1)

    # Output the JSON formatted results on stdout
    return pretty_json(
        main_fetch(konnectors)
    )


if __name__ == '__main__':
    try:
        # Debug only: Set logging level and format
        if is_in_debug_mode():
            logging.basicConfig(
                format='%(levelname)s: %(message)s',
                level=logging.INFO
            )
        print(main(sys.stdin.read()))
    except KeyboardInterrupt:
        pass
