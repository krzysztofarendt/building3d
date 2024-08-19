import numpy as np
from numba import njit

from building3d.geom.numba.types import PointType, FLOAT


@njit
def distance_point_to_edge(ptest: PointType, pt1: PointType, pt2: PointType) -> FLOAT:
    """Calculates distance of ptest to the line segment pt1->pt2."""
    v21 = pt2 - pt1
    vt1 = ptest - pt1

    # Project vt1 vector onto the line segment v21
    # t represents a value between 0 and 1 where:
    # t=0 corresponts to the start of point of the segment
    # t=1 corresponds to the end point of the segment
    t = np.dot(vt1, v21) / np.dot(v21, v21)

    # Check if the projection is outside the segment range
    if t < 0:
        # closest_point = pt1
        return np.linalg.norm(pt1 - ptest)
    elif t > 1:
        # closest_point = pt2
        return np.linalg.norm(pt2 - ptest)
    else:
        # Closest point is somewhere between pt1 and pt2
        closest_point = pt1 + t * v21
        return np.linalg.norm(closest_point - ptest)
