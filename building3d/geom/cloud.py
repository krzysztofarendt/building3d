import numpy as np

from building3d.geom.vector import normal
from building3d.geom.point import Point
from building3d.config import GEOM_EPSILON
from building3d.geom.exceptions import GeometryError


def points_to_array(pts: list[Point]) -> np.ndarray:
    """Convert a list of points to a numpy array of shape (num_points, 3)."""
    return np.array([p.vector() for p in pts])


def array_to_points(arr: np.ndarray) -> list[Point]:
    """Convert a numpy array shaped (num_points, 3) to a list of points."""
    return [Point(x[0], x[1], x[2]) for x in arr]


def are_points_in_set(pts: list[Point], are_in: list[Point]) -> bool:
    """Test if points `pts` are a subset of `are_in`."""
    pts_set = set(pts)
    are_in_set = set(are_in)
    return pts_set.issubset(are_in_set)


def are_points_coplanar(*pts: Point, tol: float = GEOM_EPSILON) -> bool:
    """Check if all points lay on the same surface."""

    if len(pts) < 3:
        raise GeometryError("Less than 3 points provided to the function")

    if len(pts) == 3:
        return True

    vec_n = normal(pts[0], pts[1], pts[2])

    # Plane equation:
    # ax + by + cz + d = 0
    # (a, b, c) are taken from the normal vector
    # d is calculated by substituting one of the points
    ref = 0  # reference point index
    ref_pt = pts[ref]
    d = -1 * (vec_n[0] * ref_pt.x + vec_n[1] * ref_pt.y + vec_n[2] * ref_pt.z)

    # Check if all points lay on the same plane
    for p in pts:
        coplanar = np.abs(vec_n[0] * p.x + vec_n[1] * p.y + vec_n[2] * p.z + d) < tol
        if not coplanar:
            return False
    return True
