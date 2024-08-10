import numpy as np
from numba import njit

from building3d.geom.numba.config import PointType, VectorType


@njit
def normal(pt0: PointType, pt1: PointType, pt2: PointType) -> VectorType:
    n = np.cross(pt1 - pt0, pt2 - pt0)
    len_n = np.linalg.norm(n)
    if np.isclose(len_n, 0):
        return np.full(3, np.nan)
    n /= len_n
    return n
