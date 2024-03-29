from building3d.geom.line import create_points_between_2_points
from building3d.geom.point import Point


def test_create_points_between_2_points():
    p1 = Point(0.0, 0.0, 0.0)
    p2 = Point(1.0, 0.0, 0.0)
    num = 5
    points = create_points_between_2_points(p1, p2, num)

    xvals = set([p.x for p in points])
    assert {0.0, 0.2, 0.4, 0.6, 0.8, 1.0} == xvals
