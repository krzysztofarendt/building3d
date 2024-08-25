import json

from collections import defaultdict


def recursive_default_dict():
    """Default dict with default dict as the default type for all nested levels."""
    return defaultdict(recursive_default_dict)


def recursive_default_dict_to_dict(rdd):
    """Convert recursive default dict to standard dict.

    Uses the `json` module, so does not support classes and functions as keys and values.
    """
    d = json.loads(json.dumps(rdd))
    return d
