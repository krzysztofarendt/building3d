import numpy as np

from building3d.geom.vector import normal
from building3d.geom.vector import is_point_colinear
from building3d.geom.point import Point
from building3d.config import GEOM_EPSILON
from building3d.geom.exceptions import GeometryError
from building3d.util.roll_back import roll_back


def points_to_array(pts: list[Point]) -> np.ndarray:
    """Convert a list of points to a numpy array with shape (num_points, 3)."""
    return np.array([p.vector() for p in pts])


def array_to_points(arr: np.ndarray) -> list[Point]:
    """Convert a numpy array shaped (num_points, 3) to a list of points."""
    return [Point(x[0], x[1], x[2]) for x in arr]


def points_to_flat_list(pts: list[Point]) -> list[float]:
    """Convert a list of points to a flattened list with length `num_points * 3`."""
    return points_to_array(pts).flatten().tolist()


def flat_list_to_points(plist: list[float]) -> list[Point]:
    """Convert a list of floats to a list of points."""
    data = np.array(plist).reshape((-1, 3))
    pts = []
    for d in data:
        pts.append(Point(d[0], d[1], d[2]))
    return pts


def points_to_nested_list(pts: list[Point]) -> list[list[float]]:
    """Convert a list of points to a nested list."""
    return points_to_array(pts).tolist()


def nested_list_to_points(plist: list[list[float]]) -> list[Point]:
    """Convert a nested list of floats to a list of points."""
    points = []
    for i in range(len(plist)):
        x = plist[i][0]
        y = plist[i][1]
        z = plist[i][2]
        points.append(Point(x, y, z))
    return points


def are_points_in_set(pts: list[Point], are_in: list[Point]) -> bool:
    """Test if points `pts` are a subset of `are_in`."""
    pts_set = set(pts)
    are_in_set = set(are_in)
    return pts_set.issubset(are_in_set)


def are_points_coplanar(*pts: Point, tol: float = GEOM_EPSILON) -> bool:
    """Check if all points lay on the same surface."""

    if len(set(pts)) <= 3:
        # If the number of unique points is less or equal 3, they must be coplanar
        return True

    vec_n = np.array([0, 0, 0])
    num_tries = 0
    max_tries = len(pts)
    while np.allclose(vec_n, 0):
        vec_n = normal(pts[0], pts[1], pts[2])
        if (np.abs(vec_n) > tol).any():
            break
        else:
            assert is_point_colinear(pts[0], pts[1], pts[2]), \
                "This case must mean they are colinear. If not, debugging needed."
            pts = tuple(roll_back(list(pts)))
        num_tries += 1
        if num_tries > max_tries:
            # All points are colinear, so they are also coplanar
            return True

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
