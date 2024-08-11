from numba import njit
import numpy as np

from building3d.geom.numba.vectors import normal
from building3d.geom.numba.types import PointType, VectorType, FLOAT


@njit
def projection_coefficients(pt: PointType, vn: VectorType) -> tuple[FLOAT, FLOAT, FLOAT, FLOAT]:
    """Returns array [a, b, c, d] from the equation ax + by + cz + d = 0.

    Uses the vector normal to a plane and the point p
    to calculate the coefficients of the plane equation
    with the same slope as this polygon, but translated to the point p.
    """
    d = -1 * np.dot(vn, pt)
    a, b, c = vn
    return a, b, c, d


@njit
def plane_coefficients(pts: PointType) -> tuple[FLOAT, FLOAT, FLOAT, FLOAT]:
    """Returns [a, b, c, d] from the equation ax + by + cz + d = 0 based on given points.

    This equation describes the plane that this polygon is on.
    """
    vn = normal(pts[-1], pts[0], pts[1])
    a, b, c, d = projection_coefficients(pts[0], vn)
    return a, b, c, d
