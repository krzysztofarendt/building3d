import numpy as np

from building3d.geom.numba.types import FLOAT


# Location constants
EXTERIOR = 0
INTERIOR = 1
VERTEX = 2
EDGE = 3
INVALID_INDEX = -1
INVALID_LOC = -2
INVALID_PT = np.full(3, np.nan, dtype=FLOAT)
