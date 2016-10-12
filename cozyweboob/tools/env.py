"""
Helper functions related to environment variables.
"""
import os


def is_in_debug_mode():
    """
    Check whether cozyweboob is running in debug mode.

    Returns:
        true / false
    """
    return (
        "COZYWEBOOB_ENV" in os.environ and
        os.environ["COZYWEBOOB_ENV"] == "debug"
    )
