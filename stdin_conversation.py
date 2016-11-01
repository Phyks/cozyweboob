#!/usr/bin/env python2
"""
Wrapper around weboob to be called from mode, in a conversation way, similar to
the
[Python-shell](https://github.com/Birch-san/python-shell/blob/9d8641dc1e55e808ba82d029f9920413ab63206f/test/python/conversation.py)
conversation example.
"""
import logging
import sys

from cozyweboob import main as cozyweboob
from cozyweboob import clean
from cozyweboob import WeboobProxy
from cozyweboob.tools.env import is_in_debug_mode
from cozyweboob.tools.jsonwriter import json_dump

# Module specific logger
logger = logging.getLogger(__name__)


def fetch_view(params):
    """
    Fetch from weboob modules.
    """
    return json_dump(cozyweboob(params))


def list_view():
    """
    List all available weboob modules and their configuration options.
    """
    proxy = WeboobProxy()
    return json_dump(proxy.list_modules())


def clean_view():
    """
    Clean temporary downloaded files.
    """
    return json_dump(clean())


def process_query(query):
    """
    Process input query on the command-line.

    Args:
        query: The query received on stdin.
    Returns:
        - A JSON response if a valid query is received.
        - False if should exit.
        - None if invalid query is received.
    """
    query = query.strip()
    if query == "GET /list":
        # List modules view
        logger.info("Calling /list view.")
        return list_view()
    elif query == "GET /clean":
        # Clean view
        logger.info("Calling /clean view")
        return clean_view()
    elif query.startswith("POST /fetch"):
        # Fetch modules view
        logger.info("Calling /fetch view.")
        params = query.split()[2]
        return fetch_view(params)
    elif query == "exit":
        # Exit command
        logger.info("Exiting.")
        return False
    else:
        # Invalid query
        logger.error("Invalid query, exiting: %s" % query)
        return


def main():
    """
    Main function
    """
    # Debug only: Set logging level and format
    if is_in_debug_mode():
        logging.basicConfig(
            format='%(levelname)s: %(message)s',
            level=logging.INFO
        )
    else:
        logging.basicConfig(
            format='%(levelname)s: %(message)s',
            level=logging.ERROR
        )
    # Ensure all modules are installed and up to date before starting the
    # server
    logger.info("Ensuring all modules are installed and up to date.")
    proxy = WeboobProxy()
    proxy.install_modules()
    logger.info("Starting server.")
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        response = process_query(line)
        if response:
            print(response)
        else:
            break
        sys.stdout.flush()


if __name__ == "__main__":
    main()
