import numpy as np

from building3d.geom.point import Point
from building3d.geom.vector import length
from building3d.config import GEOM_EPSILON



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
        num_segments = int(edge_len // (delta + GEOM_EPSILON))
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
