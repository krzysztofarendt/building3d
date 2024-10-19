import numpy as np
from numba import njit

from building3d.geom.bboxes import bounding_box
from building3d.geom.points import new_point_between_2_points
from building3d.geom.points import points_equal
from building3d.geom.polygon.ispointinside import is_point_at_boundary
from building3d.geom.polygon.ispointinside import is_point_inside
from building3d.geom.types import IndexType
from building3d.geom.types import PointType


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
    bbox1 = bounding_box(pts1)
    bbox2 = bounding_box(pts2)
    if not are_bboxes_overlapping(bbox1, bbox2):
        return False

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
def are_bboxes_overlapping(bbox1, bbox2):
    """Check if two bounding boxes are overlapping.

    This function determines if two axis-aligned bounding boxes are overlapping
    in any dimension.

    Args:
        bbox1 (tuple of points): First bounding box, represented as
                                 [[min_x, min_y, min_z], [max_x, max_y, max_z]].
        bbox2 (tuple of points): Second bounding box, represented as
                                 [[min_x, min_y, min_z], [max_x, max_y, max_z]].

    Returns:
        bool: True if the bounding boxes overlap, False otherwise.
    """
    if (bbox1[1] < bbox2[0]).any() or (bbox1[0] > bbox2[1]).any():
        return False
    else:
        return True


@njit
def are_all_points_same(pts1: PointType, pts2: PointType) -> bool:
    """Check if all points in two sets are the same.

    This function compares two sets of points and determines if they contain
    the same points, regardless of order.

    Args:
        pts1 (PointType): First set of points.
        pts2 (PointType): Second set of points.

    Returns:
        bool: True if all points in pts1 have a matching point in pts2,
              False otherwise.
    """
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
    """Check if points from polygon B touch or are inside polygon A.

    This function checks each point of polygon B against polygon A to determine
    if any points are on the boundary or inside polygon A.

    Args:
        pts_a (PointType): Points of polygon A.
        tri_a (IndexType): Triangles of polygon A.
        pts_b (PointType): Points of polygon B to check against polygon A.

    Returns:
        tuple[bool, bool]: A tuple containing two booleans:
            - First boolean: True if at least one point is on the boundary.
            - Second boolean: True if at least one point or midpoint is inside.
    """
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
