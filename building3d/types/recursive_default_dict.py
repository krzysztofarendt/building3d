from collections import defaultdict


def recursive_default_dict():
    """Default dict with default dict as the default type for all nested levels."""
    return defaultdict(recursive_default_dict)
