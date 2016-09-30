#!/usr/bin/env python2
"""
Wrapper script around Weboob to be able to use it in combination with Cozy +
Konnectors easily.

Part of this code comes from [Kresus](https://github.com/bnjbvr/kresus/)
written by bnjbvr and released under MIT.
"""
from __future__ import print_function

import collections
import getpass
import importlib
import json
import logging
import sys

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

    @staticmethod
    def list_modules(capability=None):
        """
        List all available modules and their configuration options.

        Args:
            capability: Restrict the modules list to a given capability.
        Returns: A dict mapping module names to supported capabilities and
        available configuration options.
        """
        available_modules = {}
        moduleInfos = Weboob().repositories.get_all_modules_info(capability)
        for module in moduleInfos:
            available_modules[module] = {
                "infos": dict(moduleInfos[module].dump()),
                "config": None  # TODO: Get config options from module
            }
        return available_modules

    def __init__(self, modulename, parameters):
        """
        Create a Weboob handle and try to load the modules.

        Args:
            modulename: the name of the weboob module to use.
            parameters: A dict of parameters to pass the weboob module.
        """
        # Get a weboob instance
        self.weboob = Weboob()
        # Install the module if necessary and hide the progress.
        repositories = self.weboob.repositories
        minfo = repositories.get_module_info(modulename)
        if minfo is not None and not minfo.is_installed():
            repositories.install(minfo, progress=DummyProgress())
        # Build a backend for this module
        self.backend = self.weboob.build_backend(modulename, parameters)

    def get_backend(self):
        """
        Backend getter.

        Returns:
            the built backend.
        """
        return self.backend


def mainFetch(used_modules):
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
            logger.info("Fetching data from module %s.", module["id"])
            # Get associated backend for this module
            backend = WeboobProxy(
                module["name"],
                module["parameters"]
            ).get_backend()
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
                    fetched_data[module["id"]].update(fetching_function(backend))
                except AttributeError:
                    # In case the converter does not exist on our side
                    logger.error("%s capability is not implemented.", capability)
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
            for module in range(len(konnectors)):
                for param in konnectors[module]["parameters"]:
                    if not konnectors[module]["parameters"][param]:
                        konnectors[module]["parameters"][param] = getpass.getpass(
                            "Password for module %s? " % konnectors[module]["id"]
                        )
    except ValueError:
        logger.error("Invalid JSON input.")
        sys.exit(-1)

    # Output the JSON formatted results on stdout
    return pretty_json(
        mainFetch(konnectors)
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
