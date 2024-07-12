import numpy as np

from building3d.geom.point import Point
from building3d.geom.vector import length
from building3d.config import GEOM_ATOL



def create_point_between_2_points_at_distance(
    p1: Point,
    p2: Point,
    distance: float
) -> Point:
    """Create new point along the edge spanning from p1 to p2.

    Args:
        p1: first point of the edge
        p2: second point of the edge
        distance: relative distance along the edge, 0 = p1, 1 = p2

    Return:
        new point
    """
    alpha = distance
    alpha_v = np.array([alpha, alpha, alpha])
    new_vec = p1.vector() * (1 - alpha_v) + p2.vector() * alpha_v
    return Point(new_vec[0], new_vec[1], new_vec[2])


def create_points_between_2_points(p1: Point, p2: Point, num: int) -> list[Point]:
    """Create new points along the edge spanning from p1 to p2.

    Args:
        p1: first point of the edge
        p2: second point of the edge
        num: number of new points to create

    Return:
        list of points including p1 and p2
    """
    points = [p1]

    for i in range(1, num):
        alpha = i / num
        alpha_v = np.array([alpha, alpha, alpha])
        new_vec = p1.vector() * (1 - alpha_v) + p2.vector() * alpha_v
        new_pt = Point(new_vec[0], new_vec[1], new_vec[2])
        points.append(new_pt)

    points.append(p2)

    return points


def is_point_on_segment(ptest: Point, pt1: Point, pt2: Point) -> bool:
    """
    Check if a point p lies on the line segment defined by points p1 and p2.

    Args:
        ptest: The point to check
        pt1: The first endpoint of the segment
        pt2: The second endpoint of the segment

    Returns:
        bool: True if the point lies on the segment, False otherwise.
    """
    p = ptest.vector()
    p1 = pt1.vector()
    p2 = pt2.vector()

    # Check collinearity using the cross product
    if not np.allclose(np.cross(p - p1, p2 - p1), [0, 0, 0]):
        return False

    # Check if the point lies within the segment bounds
    dot_product = np.dot(p - p1, p2 - p1)
    squared_length_p1_p2 = np.dot(p2 - p1, p2 - p1)

    if dot_product < 0 or dot_product > squared_length_p1_p2:
        return False

    return True


def create_points_between_list_of_points(
    pts: list[Point],
    delta: float,
    fixed_pts: list[Point] = [],
) -> list[Point]:
    """Add new points on the edges, but respect fixed points.

    Args:
        pts: list of input points defining the edges
        delta: approximate distance between new points
        fixed_pts: list of fixed points which must appear in the output

    Return:
        list of new points (input and fixed points included)
    """
    edge_points = []
    for i in range(len(pts)):
        cur = i
        nxt = i + 1 if i + 1 < len(pts) else 0
        pt1 = pts[cur]
        pt2 = pts[nxt]
        edge_len = length(pt2.vector() - pt1.vector())
        num_segments = int(edge_len // (delta + GEOM_ATOL))
        new_pts = create_points_between_2_points(pt1, pt2, num_segments)
        for p in new_pts:
            is_far_from_all = True
            for fp in fixed_pts:
                dist = length(p.vector() - fp.vector())
                if dist < delta:
                    is_far_from_all = False
                    break
            if is_far_from_all:
                edge_points.append(p)
    return edge_points


def distance_point_to_edge(ptest: Point, p1: Point, p2: Point) -> float:
    """Calculate distance of ptest to the line segment p1-p2."""

    line_segment = p2.vector() - p1.vector()
    to_ptest = ptest.vector() - p1.vector()

    # Project `ptest_to_p1` vector onto the line segment (edge)
    # t represents a value between 0 and 1 where:
    # t=0 corresponts to the start of point of the segment
    # t=1 corresponds to the end point of the segment
    t = np.dot(to_ptest, line_segment) / np.dot(line_segment, line_segment)

    # Check if the projection is outside the segment range
    if t < 0:
        closest_point = p1
        return length(p1.vector() - ptest.vector())
    if t > 1:
        closest_point = p2
        return length(p2.vector() - ptest.vector())
    else:
        # Closest point is somewhere between p1 and p2
        closest_point = p1 + t * line_segment
        return length(closest_point.vector() - ptest.vector())


def line_intersection(pt1: Point, d1: np.ndarray, pt2: Point, d2: np.ndarray) -> Point | None:
    """Determine the intersection point of two lines in 3D space.

    Args:
        p1: A point on the first line.
        d1: The direction vector of the first line.
        p2: A point on the second line.
        d2: The direction vector of the second line.

    Returns:
        The coordinates of the intersection point, or None if the lines are parallel or coincident.
    """
    # Convert points and direction vectors to numpy arrays
    p1 = pt1.vector()
    d1 = np.array(d1)
    p2 = pt2.vector()
    d2 = np.array(d2)

    if np.allclose(d1, [0, 0, 0]) or np.allclose(d2, [0, 0, 0]):
        # Direction vectors cannot be zero
        return None
    elif np.allclose(d1 / length(d1), d2 / length(d2)):
        # Parallel or coincident
        return None
    elif np.allclose(d1 / length(d1), -1 * d2 / length(d2)):
        # Parallel or coincident
        return None

    # Construct the system of linear equations
    A = np.array([d1, -d2]).T
    b = p2 - p1

    try:
        # Solve for t and s using least squares to handle potential overdetermined system
        t_s, _, _, s = np.linalg.lstsq(A, b, rcond=None)
        t, s = t_s

        # Check if the intersection point is the same for both lines
        point_on_line1 = p1 + t * d1
        point_on_line2 = p2 + s * d2

        if np.allclose(point_on_line1, point_on_line2):
            x, y, z = point_on_line1
            return Point(x, y, z)
        else:
            return None
    except np.linalg.LinAlgError:
        return None


def line_segment_intersection(pa1: Point, pb1: Point, pa2: Point, pb2: Point) -> Point | None:
    """Determine the intersection point between two line segments: pa1->pb1 and pa2->pb2.

    Return None if:
    - line segments are not intersecting
    - line segments are parallel or coincident (their direction vectors are equal)
    """
    d1 = pb1.vector() - pa1.vector()
    d2 = pb2.vector() - pa2.vector()

    candidate = line_intersection(pa1, d1, pa2, d2)

    if candidate is None:
        return None
    else:
        # Check if the candidate point lies within both edges
        if is_point_on_segment(candidate, pa1, pb1) and is_point_on_segment(candidate, pa2, pb2):
            return candidate
        else:
            return None
