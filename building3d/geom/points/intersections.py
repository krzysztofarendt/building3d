import numpy as np
from numba import njit

from building3d.geom.types import PointType, VectorType, INVALID_PT
from building3d.geom.vectors import new_vector
from building3d.geom.points import is_point_on_segment
from building3d.geom.points import list_pts_to_array
from building3d.geom.points import new_point


@njit
def line_intersection(
    pt1: PointType,
    d1: VectorType,
    pt2: PointType,
    d2: VectorType,
) -> PointType:
    """Determines the intersection point of two lines in 3D space.

    Args:
        pt1: A point on the first line.
        d1: The direction vector of the first line.
        pt2: A point on the second line.
        d2: The direction vector of the second line.

    Returns:
        The coordinates of the intersection point, filled with `nan`
        if the lines are parallel or coincident.
    """
    if np.allclose(d1, new_vector(0, 0, 0)) or np.allclose(d2, new_vector(0, 0, 0)):
        # Direction vectors cannot be zero
        return INVALID_PT
    elif np.allclose(d1 / np.linalg.norm(d1), d2 / np.linalg.norm(d2)):
        # Parallel or coincident
        return INVALID_PT
    elif np.allclose(d1 / np.linalg.norm(d1), -1 * d2 / np.linalg.norm(d2)):
        # Parallel or coincident
        return INVALID_PT

    # Construct the system of linear equations
    A = list_pts_to_array([d1, -d2]).T
    b = pt2 - pt1

    try:
        # Solve for t and s using least squares to handle potential overdetermined system
        # TODO: rcond=None is needed to suppress deprecation warning, but numba doesn't support it
        t_s, _, _, s = np.linalg.lstsq(A, b)
    except Exception:  # numba does not support other types of exceptions
        return INVALID_PT

    t, s = t_s

    # Check if the intersection point is the same for both lines
    point_on_line1 = pt1 + t * d1
    point_on_line2 = pt2 + s * d2

    if np.allclose(point_on_line1, point_on_line2):
        x, y, z = point_on_line1
        return new_point(x, y, z)
    else:
        return INVALID_PT


@njit
def line_segment_intersection(
    pa1: PointType,
    pb1: PointType,
    pa2: PointType,
    pb2: PointType,
) -> PointType:
    """Determines the intersection point between two line segments: pa1->pb1 and pa2->pb2.

    Returns `INVALID_PT` if:
    - line segments are not intersecting
    - line segments are parallel or coincident (their direction vectors are equal)
    """
    d1 = pb1 - pa1
    d2 = pb2 - pa2

    candidate = line_intersection(pa1, d1, pa2, d2)

    if candidate is INVALID_PT:
        return INVALID_PT
    else:
        # Check if the candidate point lies within both edges
        if is_point_on_segment(candidate, pa1, pb1) and is_point_on_segment(
            candidate, pa2, pb2
        ):
            return candidate
        else:
            return INVALID_PT
