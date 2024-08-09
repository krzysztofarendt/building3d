import numpy as np
from numba import njit

from building3d.geom.numba.config import POINT_TYPE, VECTOR_TYPE


@njit
def normal(pt0: POINT_TYPE, pt1: POINT_TYPE, pt2: POINT_TYPE) -> VECTOR_TYPE:
    n = np.cross(pt1 - pt0, pt2 - pt0)
    len_n = np.linalg.norm(n)
    if np.isclose(len_n, 0):
        return np.full(3, np.nan)
    n /= len_n
    return n
