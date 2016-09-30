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
