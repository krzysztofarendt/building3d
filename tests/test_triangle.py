from building3d.geom.point import Point
from building3d.geom.triangle import is_point_inside


def test_is_point_inside_triangle():
    p0 = Point(1.0, 0.0, 0.0)
    p1 = Point(0.0, 0.0, 0.0)
    p2 = Point(0.0, 1.0, 0.0)

    ptest = Point(0.1, 0.1, 0.0)  # inside
    assert is_point_inside(ptest, p0, p1, p2) is True

    ptest = Point(0.0, 0.0, 0.0)  # inside (at the corner)
    assert is_point_inside(ptest, p0, p1, p2) is True

    ptest = Point(1.0, 0.0, 0.0)  # inside (at the corner)
    assert is_point_inside(ptest, p0, p1, p2) is True

    ptest = Point(0.5, 0.5, 0.0)  # inside (on the edge)
    assert is_point_inside(ptest, p0, p1, p2) is True

    ptest = Point(0.51, 0.51, 0.0)  # outside
    assert is_point_inside(ptest, p0, p1, p2) is False

    p0 = Point(0.6, 0.0, 0.0)
    p1 = Point(0.0, 0.0, 0.0)
    p2 = Point(0.0, 0.6, 0.0)

    ptest = Point(0.3, 0.3, 0.0)  # inside (on the edge)
    assert is_point_inside(ptest, p0, p1, p2) is True
