"""
Miscellaneous progress functions.
"""


class DummyProgress:
    """
    Dummy progress bar, to disable it.
    """
    def progress(self, *args):
        """
        Progress function. Do nothing.
        """
        pass

    def error(self, message):
        """
        Error function. Do nothing.
        """
        pass

    def prompt(self, message):
        """
        Prompt function. Not implemented.
        """
        raise NotImplementedError()
