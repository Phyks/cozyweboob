"""
Helper functions related to Weboob-specific code.
"""
from weboob.tools.value import (ValueBackendPassword, ValueInt, ValueFloat,
                                ValueBool)


def value_to_string(value):
    """
    Convert a Value definition from Weboob to a string describing the field
    type.

    Args:
        value: A Weboob value definition.
    Returns: A string describing the value type.
    """
    if isinstance(value, ValueBackendPassword):
        return "password"
    elif isinstance(value, ValueInt):
        return "int"
    elif isinstance(value, ValueFloat):
        return "float"
    elif isinstance(value, ValueBool):
        return "bool"
    else:
        return "text"


def dictify_config_desc(config):
    """
    Convert a Weboob BackendConfig description to a JSON-serializabe dict.

    Args:
        config: A Weboob BackendConfig object.
    Returns: A JSON-serializable dict.
    """
    return {
        name: value_to_string(value)
        for name, value in config.items()
    }
