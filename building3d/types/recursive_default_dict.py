import json
from collections import defaultdict


def recursive_default_dict():
    """Default dict with default dict as the default type for all nested levels.

    How it works:
    - if the key is present, it returns the associated value
    - if the key is not present, it sets the value to a new default_dict()

    Example:
        >>> d = recursive_default_dict()
        >>> d['a']['b']['c'] = 1  # Creates nested dicts automatically
        >>> print(d['a']['b']['c'])  # Prints: 1
        >>> print(d['x']['y'])  # Creates empty dict, no KeyError
        defaultdict(<function recursive_default_dict ...>, {})
    """
    return defaultdict(recursive_default_dict)


def recursive_default_dict_to_dict(rdd):
    """Convert recursive default dict to standard dict.

    Uses the `json` module, so does not support classes and functions as keys and values.

    Example:
        >>> d = recursive_default_dict()
        >>> d['a']['b'] = 1
        >>> d['x']['y'] = {'z': 2}
        >>> regular_dict = recursive_default_dict_to_dict(d)
        >>> print(regular_dict)
        {'a': {'b': 1}, 'x': {'y': {'z': 2}}}
        >>> type(regular_dict)
        <class 'dict'>
    """
    d = json.loads(json.dumps(rdd))
    return d
