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
        return json.JSONEncoder.default(self, o)


def pretty_json(foo):
    """
    Pretty printing of JSON output, using the custom JSONEncoder.
    """
    return json.dumps(foo, sort_keys=True,
                      indent=4, separators=(',', ': '),
                      cls=CustomJSONEncoder)
