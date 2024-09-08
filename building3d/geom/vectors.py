import numpy as np
from numba import njit

from building3d.geom.types import PointType, VectorType, FLOAT


@njit
def new_vector(x: float, y: float, z: float) -> VectorType:
    return np.array([x, y, z], dtype=FLOAT)


@njit
def normal(pt0: PointType, pt1: PointType, pt2: PointType) -> VectorType:
    """Calculates vector normal to the surface defined with 3 points.

    If the normal does not exist, returns `np.full(3, np.nan)`.
    The normal might not exist e.g. if the points are collinear.
    """
    vn = np.cross(pt1 - pt0, pt2 - pt0)
    len_vn = np.linalg.norm(vn)
    if np.isclose(len_vn, 0):
        return np.full(3, np.nan, dtype=FLOAT)
    vn = vn / len_vn
    return vn


@njit
def angle(v1: VectorType, v2: VectorType) -> FLOAT:
    """Calculates angle in radians between two vectors."""
    dot_v1_v2 = np.dot(v1 / np.linalg.norm(v1), v2 / np.linalg.norm(v2))

    # Clip to [-1, 1]
    # numba doesn't support np.clip for scalars, so it has to be done manually
    if dot_v1_v2 > 1.0:
        dot_v1_v2 = 1.0
    elif dot_v1_v2 < -1.0:
        dot_v1_v2 = -1.0

    rad = np.arccos(dot_v1_v2)
    if rad < 0:
        rad = 2.0 * np.pi + rad

    return rad
