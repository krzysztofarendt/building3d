import numpy as np

from .point import Point


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
