"""
This module implements a custom JSON writer to be able to serialize data
returned by Weboob and pretty print the output JSON.

Based upon
http://stackoverflow.com/questions/11875770/how-to-overcome-datetime-datetime-not-json-serializable-in-python.
"""
import json

from datetime import date, datetime
from decimal import Decimal


class CustomJSONEncoder(json.JSONEncoder):
    """
    Custom JSONEncoder to support more types.
    """
    def default(self, o):
        if isinstance(o, datetime) or isinstance(o, date):
            # Serialize datetime objects to ISO dates
            return o.isoformat()
        elif isinstance(o, Decimal):
            # Serialize Decimal objects to string
            return str(o)
        elif isinstance(o, Exception):
            # Serialize Exception objects to string representation
            return repr(o)
        return json.JSONEncoder.default(self, o)


def pretty_json(obj):
    """
    Pretty printing of JSON output, using the custom JSONEncoder.

    Args:
        obj: the object to JSON serialize.
    Returns:
        the pretty printed JSON string.
    """
    return json.dumps(obj, sort_keys=True,
                      indent=4, separators=(',', ': '),
                      cls=CustomJSONEncoder)
