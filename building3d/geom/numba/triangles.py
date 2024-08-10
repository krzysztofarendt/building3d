from numba import njit
import numpy as np

from building3d.geom.exceptions import GeometryError
from building3d.config import EPSILON
from building3d.config import GEOM_ATOL
from building3d.config import POINT_NUM_DEC
from .config import PointType, VectorType


@njit
def triangle_area(pt1: PointType, pt2: PointType, pt3: PointType) -> float:
    """Calculates triangle area using the Heron's formula.

    Reference: https://en.wikipedia.org/wiki/Heron%27s_formula
    """
    va = pt2 - pt1
    vb = pt3 - pt2
    vc = pt3 - pt1
    a = np.linalg.norm(va)
    b = np.linalg.norm(vb)
    c = np.linalg.norm(vc)

    s = 0.5 * (a + b + c)
    area = np.sqrt(s * (s - a) * (s - b) * (s - c) + EPSILON)

    return area


@njit
def triangle_centroid(pt1: PointType, pt2: PointType, pt3: PointType) -> PointType:
    """Calculates triangle's centroid. It is simply a mean of its vertices."""
    return (pt1 + pt2 + pt3) / 3.0


@njit
def is_point_on_same_side(
    pt1: PointType,
    pt2: PointType,
    ptest: PointType,
    ptref: PointType,
    atol: float = GEOM_ATOL,
) -> bool:
    """Tests if ptest is on the same side of the vector p1->p2 as ptref.

    Args:
        pt1: first vertex of the vector
        pt2: second vertex of the vector
        ptest: tested point (does it lie on the same side as ptref?)
        ptref: reference point
        atol: absolute tolerance

    Returns:
        True if ptest is on the same side as ptref

    Raises:
        GeometryError
    """
    vtest = np.cross(pt2 - pt1, ptest - pt1)
    vref = np.cross(pt2 - pt1, ptref - pt1)

    len_vtest = np.linalg.norm(vtest)
    len_vref = np.linalg.norm(vref)

    if len_vref < atol:
        # Wrong reference point chosen (collinear with p1 and p2)
        raise GeometryError("Wrong reference point chosen (colinear with p1 and p2)")
    elif len_vtest < atol:
        # This point lies on the edge connecting p1 and p2
        return False
    else:
        vtest /= len_vtest
        vref /= len_vref
        return bool(np.isclose(vtest, vref).all())
