"""
Main script for this module
"""
from __future__ import absolute_import
from __future__ import print_function

import collections
import importlib
import json
import logging
import os
import shutil
import sys
import tempfile

from getpass import getpass

from requests.utils import dict_from_cookiejar

from cozyweboob.WeboobProxy import WeboobProxy
from cozyweboob.tools.env import is_in_debug_mode
from cozyweboob.tools.jsonwriter import pretty_json


# Module specific logger
logger = logging.getLogger(__name__)

# Dynamically load capabilities conversion modules
# Dynamic loading is required to be able to call them programatically.
CAPABILITIES_CONVERSION_MODULES = importlib.import_module(".capabilities",
                                                          package="cozyweboob")


def clean():
    """
    Delete all the temporary downloaded files. These are the
    "cozyweboob-*-tmp" folders in your system tmp dir.
    """
    sys_tmp_dir = tempfile.gettempdir()
    tmp_dirs = [
        x
        for x in os.listdir(sys_tmp_dir)
        if os.path.isdir(os.path.join(sys_tmp_dir, x))
    ]
    removed_dirs = []
    for tmp_dir in tmp_dirs:
        if tmp_dir.startswith("cozyweboob-") and tmp_dir.endswith("-tmp"):
            tmp_dir = os.path.join(sys_tmp_dir, tmp_dir)
            removed_dirs.append(tmp_dir)
            shutil.rmtree(tmp_dir)
    return {
        "removed_dirs": removed_dirs
    }


def main_fetch(used_modules):
    """
    Main fetching code

    Args:
        used_modules: A list of modules description dicts.
    Returns: A dict of all the results, ready to be JSON serialized.
    """
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
                        fetching_function(
                            backend,
                            # If no actions specified, fetch but don't download
                            module.get("actions", {
                                "fetch": True,
                                "download": False
                            })
                        )
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
        except Exception as exception:
            # Store any error happening in a dedicated field
            fetched_data[module["id"]]["error"] = exception
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
