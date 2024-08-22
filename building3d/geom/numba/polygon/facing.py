from numba import njit
import numpy as np

from building3d.config import GEOM_RTOL
from building3d.geom.numba.points import points_equal
from building3d.geom.numba.types import PointType, VectorType, IndexType
from building3d.geom.numba.points import are_points_coplanar
from building3d.geom.numba.polygon.ispointinside import is_point_inside
from building3d.geom.numba.polygon.area import polygon_area
from building3d.geom.numba.polygon.touching import are_polygons_touching


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

    normals_opposite = True


    num_matching = 0
    matched = set()
    # This does not test if the connections between points are same
    # So it tests also if the areas are the same
    # TODO: There might still be rare cases where it gives incorrect solutions
    for i in range(pts1.shape[0]):
        for j in range(pts2.shape[0]):
            if j not in matched:
                if points_equal(pts1[i], pts2[j]):
                    num_matching += 1
                    matched.add(j)
                    break
    if num_matching == len(pts1):
        if np.isclose(polygon_area(pts1, vn1), polygon_area(pts2, vn2)):
            return True
    else:
        if exact is True:
            return False
        else:
            pass

    # Condition 1: points must be  coplanar
    points_coplanar = are_points_coplanar(np.vstack((pts1, pts2)))

    # Condition 2: normal vectors must be opposite
    pass  # Already checked at the beginning

    # Condition 3: polygons must not be touching (touching = shared boundary but not overlapping)
    touching = are_polygons_touching(pts1, tri1, pts2, tri2)
    if touching:
        return False

    # Condition 4: polygons must be overlapping
    overlapping = False
    for pt in pts1:
        if is_point_inside(pt, pts2, tri2, boundary_in=True):
            overlapping = True
            break
    if not overlapping:
        for pt in pts2:
            if is_point_inside(pt, pts1, tri1, boundary_in=True):
                overlapping = True
                break

    if points_coplanar and normals_opposite and overlapping and not touching:
        return True
    else:
        return False
