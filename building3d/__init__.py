import uuid

import numpy as np


def random_id(size: int | None = None) -> str:
    """Return UUID or a random string.

    If `size` is given, the hyphens are removed from the UUID
    and the first `size` characters are returned.
    If `size` is `None`, the full UUID is returned.

    When `size` is given, the maximum length of the output is 32.
    When `size` is `None`, the maximum length of the output is 36,
    because UUIDs have 4 additional hyphens.
    """
    uid = str(uuid.uuid4())
    if size is None:
        return uid
    else:
        uid = uid.replace("-", "")
        return uid[:size]


def random_within(lim=1.0):
    """Return random float within range (-lim, +lim)"""
    if lim == 0:
        return 0.0
    else:
        return 2 * lim * (np.random.random() - 0.5)
