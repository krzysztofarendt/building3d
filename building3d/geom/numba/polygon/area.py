from numba import njit
import numpy as np

from building3d.geom.numba.types import PointType, VectorType, FLOAT


@njit
def polygon_area(pts: PointType, vn: VectorType) -> float:
    """Calculates the area of a polygon.

    Calculated using the Stoke's theorem:
    https://en.wikipedia.org/wiki/Stokes%27_theorem

    Code based on:
    https://stackoverflow.com/questions/12642256/find-area-of-polygon-from-xyz-coordinates
    """
    num_pts = pts.shape[0]

    if num_pts < 3:
        return 0  # polygon with less than 3 points is not valid, assume null area

    total = np.zeros(3, dtype=FLOAT)

    for i in range(num_pts):
        pt1 = pts[i]
        if i == num_pts - 1:
            pt2 = pts[0]
        else:
            pt2 = pts[i+1]

        total += np.cross(pt1, pt2)

    area = np.dot(total, vn)
    area = abs(area / 2.0)

    return float(area)
