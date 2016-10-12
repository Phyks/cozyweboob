#!/usr/bin/env python2
"""
HTTP server wrapper around weboob
"""
import logging
import os
import shutil
import tempfile

from bottle import post, request, route, run, static_file

from cozyweboob import main as cozyweboob
from cozyweboob import WeboobProxy
from cozyweboob.tools.env import is_in_debug_mode

# Module specific logger
logger = logging.getLogger(__name__)


@post("/fetch")
def fetch_view():
    """
    Fetch from weboob modules.
    """
    params = request.forms.get("params")
    return cozyweboob(params)


@post("/retrieve")
def retrieve_view():
    """
    Retrieve a previously downloaded file from weboob modules.

    Note: Beware, this route is meant to be used in a controlled development
    environment and can result in leakage of information from your temp
    default directory.
    """
    path = request.forms.get("path")
    return static_file(path.replace(tempfile.gettempdir(), './'),
                       tempfile.gettempdir(),
                       download=True)


@route("/clean")
def clean_view():
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


@route("/list")
def list_view():
    """
    List all available weboob modules and their configuration options.
    """
    proxy = WeboobProxy()
    return proxy.list_modules()


def init():
    """
    Init function
    """
    # Debug only: Set logging level and format
    if is_in_debug_mode():
        logging.basicConfig(
            format='%(levelname)s: %(message)s',
            level=logging.INFO
        )
    # Ensure all modules are installed and up to date before starting the
    # server
    logger.info("Ensuring all modules are installed and up to date.")
    proxy = WeboobProxy()
    proxy.install_modules()
    logger.info("Starting server.")


def main():
    """
    Main function
    """
    init()
    # Get host to listen on
    HOST = os.environ.get("COZYWEBOOB_HOST", "localhost")
    PORT = os.environ.get("COZYWEBOOB_PORT", 8080)
    run(host=HOST, port=PORT, debug=is_in_debug_mode())


if __name__ == "__main__":
    main()
