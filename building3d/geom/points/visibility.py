from numba import njit
import numpy as np

from building3d.geom.types import PointType, FLOAT
from building3d.geom.points import is_valid_pt
from building3d.geom.points import points_equal
from building3d.geom.points import are_points_coplanar
from building3d.geom.points.intersections import line_segment_intersection


@njit
def visibility_matrix(pts, *block_edges):
    """Checks visibility in 2D between each pair of points test points.

    Multiple blocking edges possible.

    Args:
        pts: array of test points
        block_edges: any number of arrays with edges blocking visibility

    Return:
        visibility array, shape `(num_pts, num_pts)`, filled with `0`s and `1`s
    """
    assert are_points_coplanar(pts), "This function works only with coplanar points"

    num_pts = pts.shape[0]
    vis_matrix = np.eye(num_pts, dtype=FLOAT)

    for i in range(num_pts):
        for j in range(i + 1, num_pts):
            vis_matrix[i, j] = are_points_visible(pts[i], pts[j], *block_edges)

    # Reflect symmetrically across the diagonal
    for i in range(num_pts):
        for j in range(0, i):
            vis_matrix[i, j] = vis_matrix[j, i]

    return vis_matrix


@njit
def are_points_visible(pt0: PointType, pt1: PointType, *block_edges: PointType) -> int:
    visible = 1
    not_visible = 0
    for bed in block_edges:
        for e0, e1 in bed:
            if (
                points_equal(e0, pt0)
                or points_equal(e0, pt1)
                or points_equal(e1, pt0)
                or points_equal(e1, pt1)
            ):
                continue
            else:
                int_pt = line_segment_intersection(pt0, pt1, e0, e1)
                if is_valid_pt(int_pt):
                    return not_visible
    return visible
