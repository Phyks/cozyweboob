"""
Common conversion functions for all the available capabilities.
"""
from weboob.capabilities.base import empty


def clean_object(obj, base_url=None):
    """
    Helper to get nice JSON-serializable objects from the fields of any Weboob
    object deriving from BaseObject.

    Args:
        obj: The object to handle.
        base_url: An optional base url to generate full URLs in output dict.
    Returns:
        a JSON-serializable dict for the input object.
    """
    # Convert object to a dict of its fields
    obj = obj.to_dict()
    # Clean the various fields to be JSON-serializable
    for key, value in obj.items():
        if empty(value):
            # Replace empty values by None, avoid "NotLoaded is not
            # serializable" error
            obj[key] = None
        elif key == "url" and base_url:
            # Render full absolute URLs
            obj[key] = base_url + value
    return obj
