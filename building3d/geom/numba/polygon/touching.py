from numba import njit
import numpy as np

from building3d.geom.numba.points import new_point_between_2_points, points_equal
from building3d.geom.numba.polygon.ispointinside import is_point_at_boundary
from building3d.geom.numba.polygon.ispointinside import is_point_inside
from building3d.geom.numba.types import PointType, IndexType


@njit
def are_polygons_touching(
    pts1: PointType,
    tri1: IndexType,
    pts2: PointType,
    tri2: IndexType,
) -> bool:
    """Checks if two polygons are touching (but not crossing).

    Iterates over points in `pts1` and `pts2` and checks if:
    - there is no point inside the other polygon
    - at least one point is exactly on the boundary of the other polygon

    Args:
        pts1: points of first polygon
        tri1: triangles of first polygon
        pts2: points of second polygon
        tri2: triangles of second polygon

    Returns:
        True if polygons are touching
    """
    if are_all_points_same(pts1, pts2):
        return False

    ab_touch, ab_inside = check_poly_a_against_b(pts1, tri1, pts2)
    ba_touch, ba_inside = check_poly_a_against_b(pts2, tri2, pts1)

    if ab_inside or ba_inside:
        # If any point is inside another polygon, they are crossing
        return False
    elif ab_touch or ba_touch:
        return True

    # Not touching, not not crossing
    return False


@njit
def are_all_points_same(pts1: PointType, pts2: PointType) -> bool:
    num_matching = 0
    matched = set()

    for i in range(pts1.shape[0]):
        for j in range(pts2.shape[0]):
            if j not in matched:
                if points_equal(pts1[i], pts2[j]):
                    num_matching += 1
                    matched.add(j)
                    break
    if num_matching == len(pts1):
        return True
    else:
        return False


@njit
def check_poly_a_against_b(
    pts_a: PointType,
    tri_a: IndexType,
    pts_b: PointType,
) -> tuple[bool, bool]:

    at_least_one_boundary = False
    at_least_one_inside = False
    edge = [pts_b[-1]]

    for ptest in pts_b:
        edge.append(ptest)

        is_middle_inside = False

        for x in np.linspace(0, 1, 5):
            mid_pt = new_point_between_2_points(edge[0], edge[1], rel_d=x)
            if is_point_inside(mid_pt, pts_a, tri_a, boundary_in=False):
                is_middle_inside = True
                break

        at_boundary = is_point_at_boundary(ptest, pts_a)
        is_inside = is_point_inside(ptest, pts_a, tri_a, boundary_in=False)

        if at_boundary:
            at_least_one_boundary = True
        if is_middle_inside or is_inside:
            at_least_one_inside = True

        edge.pop(0)

    return at_least_one_boundary, at_least_one_inside
