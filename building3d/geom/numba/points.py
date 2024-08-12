import numpy as np
from numba import njit

from building3d.config import GEOM_ATOL
from building3d.config import POINT_NUM_DEC
from building3d.geom.numba.types import PointType, VectorType, FLOAT
from building3d.geom.numba.vectors import normal, new_vector


@njit
def new_point(x: float, y: float, z: float) -> PointType:
    return np.array([x, y, z], dtype=FLOAT)


# njit doesn't support f-strings
def point_to_str(pt: np.ndarray) -> str:
    """Returns a string representation of the point."""
    assert pt.shape == (3, ), "point_to_str() works only with single points."
    return f"pt(x={pt[0]:.2f},y={pt[1]:.2f},z={pt[2]:.2f},id={hex(id(pt))})"


@njit
def points_equal(pt1: PointType, pt2: PointType, atol: float = GEOM_ATOL) -> bool:
    """Checks if two points are equal."""
    return np.allclose(pt1, pt2, atol=atol)


# njit doesn't support hash() and tuple()
def point_to_hash(pt: PointType, decimals: int = POINT_NUM_DEC) -> int:
    """Calculates a hash value for the point, assuming a chosen number of decimals."""
    pt = np.round(pt, decimals=decimals)
    return hash(tuple(pt))


@njit
def are_points_coplanar(
    pts: PointType,
    atol: float = GEOM_ATOL,
) -> bool:
    """Checks if (multiple) points are coplanar.

    Args:
        pts: point array, shape (num_points, 3)
        atol: absolute tolerance

    Returns:
        True if points are coplanar, else False
    """
    num_pts = pts.shape[0]
    if num_pts <= 3:
        return True

    if are_points_collinear(pts):
        return True  # collinear points are also coplanar

    # Calculate normal vector based on the first 3 points
    # vec_n = np.full(3, np.nan, dtype=FLOAT)
    vec_n = new_vector(np.nan, np.nan, np.nan)
    i = 0
    while np.isnan(vec_n).any():
        if i+2 >= num_pts:
            if are_points_coplanar(pts):
                return True
            else:
                raise RuntimeError("Points not coplanar, yet all normal vectors have zero length")

        vec_n = normal(pts[i], pts[i+1], pts[i+2])
        i += 1

    # Plane equation:
    # ax + by + cz + d = 0
    # (a, b, c) are taken from the normal vector
    # d is calculated by substituting one of the points
    ref = 0  # reference point index
    ref_pt = pts[ref]
    d = -1 * np.dot(vec_n, ref_pt)

    # Check if all points lay on the same plane
    for i in range(num_pts):
        coplanar = np.abs(d + np.dot(vec_n, pts[i])) < atol
        if not coplanar:
            return False
    return True


@njit
def are_points_collinear(
    pts: PointType,
    atol: float = GEOM_ATOL,
) -> bool:
    """Checks if (multiple) points are collinear.

    Args:
        pts: point array, shape (num_points, 3)
        atol: absolute tolerance

    Returns:
        True if points are collinear, else False
    """
    num_pts = pts.shape[0]
    assert num_pts >= 3, "At least 3 points must be given"

    # Calculate unit vectors using the first point as origin
    vectors = np.zeros((num_pts - 1, 3))
    for i in range(1, num_pts):
        v_num = i - 1
        vectors[v_num] = pts[i] - pts[0]
        vectors[v_num] /= np.linalg.norm(vectors[v_num])

    are_collinear = True
    num_vectors = vectors.shape[0]
    for i in range(1, num_vectors):
        if (
            np.allclose(vectors[i], vectors[i-1], atol=atol)
            or
            np.allclose(vectors[i], -1 * vectors[i-1], atol=atol)
        ):
            pass
        else:
            are_collinear = False
            break

    return are_collinear


@njit
def roll_forward(pts: PointType) -> PointType:
    """Rolls points array 1 element forward. Moves the last point to the beggining.

    Returns a new object. This function does not modify `pts` in place.

    Args:
        pts: points array, shape (num_points, 3)

    Returns:
        points array shifted by 1
    """
    assert len(pts.shape) == 2
    new_pts = np.zeros(pts.shape, dtype=FLOAT)
    num_pts = pts.shape[0]
    for i in range(num_pts):
        if i == 0:
            new_pts[i] = pts[-1]
        else:
            new_pts[i] = pts[i-1]
    return new_pts


@njit
def new_point_between_2_points(
    pt1: PointType,
    pt2: PointType,
    rel_d: float
) -> PointType:
    """Creates new point along the edge pt1->pt2.

    Args:
        pt1: first point of the edge, shape (3, )
        pt2: second point of the edge, shape (3, )
        rel_d: relative distance along the edge, 0 = p1, 1 = p2

    Returns:
        new point, shape (3, )
    """
    alpha = rel_d
    alpha_v = new_vector(alpha, alpha, alpha)
    new_vec = pt1 * (1 - alpha_v) + pt2 * alpha_v
    return new_point(new_vec[0], new_vec[1], new_vec[2])


@njit
def many_new_points_between_2_points(
    pt1: PointType,
    pt2: PointType,
    num: int,
) -> PointType:
    """Creates new points along the edge spanning from p1 to p2.

    Points are evenly distributed based on `num`.

    Args:
        p1: first point of the edge, shape (3, )
        p2: second point of the edge, shape (3, )
        num: number of new points to create

    Returns:
        array of points including p1 and p2, shape (num + 2, 3)
    """
    pts = np.zeros((num + 2, 3), dtype=FLOAT)
    pts[0] = pt1

    for i in range(1, num + 1):
        alpha = i / (num + 1)
        alpha_v = new_vector(alpha, alpha, alpha)
        new_vec = pt1 * (1 - alpha_v) + pt2 * alpha_v
        new_pt = new_point(new_vec[0], new_vec[1], new_vec[2])
        pts[i] = new_pt

    pts[-1] = pt2

    return pts


@njit
def is_point_on_segment(ptest: PointType, pt1: PointType, pt2: PointType) -> bool:
    """Checks if point p lies on the line segment defined by points pt1 and pt2.

    Args:
        ptest: The point to check
        pt1: The first endpoint of the segment
        pt2: The second endpoint of the segment

    Returns:
        bool: True if the point lies on the segment, False otherwise.
    """
    # Check collinearity using the cross product
    if not np.allclose(np.cross(ptest - pt1, pt2 - pt1), np.zeros(3, dtype=FLOAT)):
        return False

    # Check if the point lies within the segment bounds
    dot_product = np.dot(ptest - pt1, pt2 - pt1)
    squared_length_p1_p2 = np.dot(pt2 - pt1, pt2 - pt1)

    if dot_product < 0 or dot_product > squared_length_p1_p2:
        return False

    return True


# TODO: njit
def create_points_between_list_of_points(
    pts: PointType,
    delta: float,
    fixed_pts: PointType | None = None,
) -> PointType:
    """Adds new points on the edges, but respects fixed points.

    Args:
        pts: array of input points defining the edges, shape (num_pts, 3)
        delta: approximate distance between new points
        fixed_pts: optional array of fixed points passed to the output, shape (num_pts, 3)

    Returns:
        array of new points (input and fixed points included), shape (num_pts, 3)
    """
    raise NotImplementedError


@njit
def distance_point_to_edge(ptest: PointType, pt1: PointType, pt2: PointType) -> float:
    """Calculates distance of ptest to the line segment pt1->pt2."""
    v21 = pt2 - pt1
    vt1 = ptest - pt1

    # Project vt1 vector onto the line segment v21
    # t represents a value between 0 and 1 where:
    # t=0 corresponts to the start of point of the segment
    # t=1 corresponds to the end point of the segment
    t = np.dot(vt1, v21) / np.dot(v21, v21)

    # Check if the projection is outside the segment range
    if t < 0:
        closest_point = pt1
        return float(np.linalg.norm(pt1 - ptest))
    elif t > 1:
        clocset_point = pt2
        return float(np.linalg.norm(pt2 - ptest))
    else:
        # Closest point is somewhere between pt1 and pt2
        closest_point = pt1 + t * v21
        return float(np.linalg.norm(closest_point - ptest))


# TODO: njit
def line_intersection(
    pt1: PointType,
    d1: VectorType,
    pt2: PointType,
    d2: VectorType,
) -> PointType | None:
    """Determines the intersection point of two lines in 3D space.

    Args:
        p1: A point on the first line.
        d1: The direction vector of the first line.
        p2: A point on the second line.
        d2: The direction vector of the second line.

    Returns:
        The coordinates of the intersection point, or None if the lines are parallel or coincident.
    """
    raise NotImplementedError


# TODO: njit
def line_segment_intersection(
    pa1: PointType,
    pb1: PointType,
    pa2: PointType,
    pb2: PointType,
) -> PointType | None:
    """Determines the intersection point between two line segments: pa1->pb1 and pa2->pb2.

    Returns None if:
    - line segments are not intersecting
    - line segments are parallel or coincident (their direction vectors are equal)
    """
    raise NotImplementedError
