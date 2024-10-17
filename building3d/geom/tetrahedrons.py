import numpy as np
from numba import njit

from building3d.config import EPSILON
from building3d.geom.types import FLOAT
from building3d.geom.types import PointType


@njit
def tetrahedron_volume(
    pt0: PointType,
    pt1: PointType,
    pt2: PointType,
    pt3: PointType,
) -> FLOAT:
    """Calculates volume using the Cayley-Menger formula."""
    # Edge lengths
    a = np.linalg.norm(pt1 - pt0)
    b = np.linalg.norm(pt2 - pt0)
    c = np.linalg.norm(pt3 - pt0)
    d = np.linalg.norm(pt2 - pt1)
    e = np.linalg.norm(pt3 - pt2)
    f = np.linalg.norm(pt3 - pt1)

    x = b**2 + c**2 - e**2
    y = a**2 + c**2 - f**2
    z = a**2 + b**2 - d**2

    nominator = (
        4 * a**2 * b**2 * c**2 - a**2 * x**2 - b**2 * y**2 - c**2 * z**2 + x * y * z
    )
    vol = np.sqrt(nominator + EPSILON) / 12.0

    return vol


@njit
def tetrahedron_centroid(
    pt0: PointType,
    pt1: PointType,
    pt2: PointType,
    pt3: PointType,
) -> PointType:
    """Centroid of a tetrahedron is just the average of its vertices."""
    ctr = (pt0 + pt1 + pt2 + pt3) / 4.0
    return ctr
