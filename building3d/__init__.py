import uuid

import numpy as np


def random_id() -> str:
    return str(uuid.uuid4())


def random_within(lim=1.0):
    """Return random float within range (-lim, +lim)"""
    if lim == 0:
        return 0.0
    else:
        return 2 * lim * (np.random.random() - 0.5)
