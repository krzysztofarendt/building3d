from numba import njit
import numpy as np

from building3d.config import GEOM_RTOL
from building3d.geom.numba.points import points_equal
from building3d.geom.numba.types import PointType, VectorType, IndexType
from building3d.geom.numba.points import are_points_coplanar
from building3d.geom.numba.polygon.ispointinside import is_point_inside


@njit
def are_polygons_facing(
    pts1: PointType,
    tri1: IndexType,
    vn1: VectorType,
    pts2: PointType,
    tri2: IndexType,
    vn2: VectorType,
    exact: bool = True,
) -> bool:
    """Checks if two polygons are facing each other.

    Returns True if all points of two polygons are equal and their normals
    are pointing towards each other.

    If exact is True, all points of two polygons must be equal (order may be different).
    If exact is False, the method checks only if polygons are overlapping, points are coplanar
    and normal vectors are opposite.

    Args:
        poly: another polygon
        exact: if True, all points of adjacent polygons must be equal

    Return:
        True if the polygons are facing each other
    """
    if not np.allclose(vn1, -1 * vn2, rtol=GEOM_RTOL):
        return False

    if exact:
        if len(pts1) != len(pts2):
            return False

        num_matching = 0
        for i in range(pts1.shape[0]):
            for j in range(pts2.shape[0]):
                if points_equal(pts1[i], pts2[j]):
                    num_matching += 1
        if num_matching == len(pts1):
            return True
        else:
            return False

    else:
        # Condition 1: points must be  coplanar
        points_coplanar = are_points_coplanar(np.vstack((pts1, pts2)))

        # Condition 2: normal vectors must be opposite
        normals_opposite = np.allclose(vn1, -1 * vn2, rtol=GEOM_RTOL)

        # Condition 3: polygons must be overlapping
        overlapping = False
        for pt in pts1:
            if is_point_inside(pt, pts2, tri2):
                overlapping = True
                break
        if not overlapping:
            for pt in pts2:
                if is_point_inside(pt, pts1, tri1):
                    overlapping = True
                    break

        if points_coplanar and normals_opposite and overlapping:
            return True
        else:
            return False
