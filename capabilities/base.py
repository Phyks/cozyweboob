from weboob.capabilities.base import empty


def clean_object(o):
    """
    Returns a JSON-serializable dict from a Weboob object.
    """
    o = o.to_dict()
    for k, v in o.items():
        if empty(v):
            # Replace empty values by None, avoid "NotLoaded is not
            # serializable" error
            o[k] = None
    return o
