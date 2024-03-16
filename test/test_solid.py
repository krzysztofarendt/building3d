import pytest

from building3d.geom.exceptions import GeometryError
from building3d.geom.point import Point
from building3d.geom.polygon import Polygon
from building3d.geom.solid import Solid


def test_correct_space_geometry():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    p4 = Point(0.0, 0.0, 1.0)
    p5 = Point(1.0, 0.0, 1.0)
    p6 = Point(1.0, 1.0, 1.0)
    p7 = Point(0.0, 1.0, 1.0)

    floor = Polygon([p0, p3, p2, p1])
    wall0 = Polygon([p0, p1, p5, p4])
    wall1 = Polygon([p1, p2, p6, p5])
    wall2 = Polygon([p3, p7, p6, p2])
    wall3 = Polygon([p0, p4, p7, p3])
    ceiling = Polygon([p4, p5, p6, p7])

    _ = Solid([floor, wall0, wall1, wall2, wall3, ceiling])


def test_points_not_shared_by_2_walls():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    p4 = Point(0.0, 0.0, 1.0)
    p5 = Point(1.0, 0.0, 1.0)
    p6 = Point(1.0, 1.0, 1.0)
    p7 = Point(0.0, 1.0, 1.0)
    p4err = Point(0.0, 0.0, 2.0)
    p5err = Point(1.0, 0.0, 2.0)
    p6err = Point(1.0, 1.0, 2.0)
    p7err = Point(0.0, 1.0, 2.0)

    floor = Polygon([p0, p3, p2, p1])
    wall0 = Polygon([p0, p1, p5, p4])
    wall1 = Polygon([p1, p2, p6, p5])
    wall2 = Polygon([p3, p7, p6, p2])
    wall3 = Polygon([p0, p4, p7, p3])
    # Make ceiling too high (not attached to walls)
    ceiling = Polygon([p4err, p5err, p6err, p7err])

    with pytest.raises(GeometryError):
        _ = Solid([floor, wall0, wall1, wall2, wall3, ceiling])


def test_point_inside():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    p4 = Point(0.0, 0.0, 1.0)
    p5 = Point(1.0, 0.0, 1.0)
    p6 = Point(1.0, 1.0, 1.0)
    p7 = Point(0.0, 1.0, 1.0)

    floor = Polygon([p0, p3, p2, p1])
    wall0 = Polygon([p0, p1, p5, p4])
    wall1 = Polygon([p1, p2, p6, p5])
    wall2 = Polygon([p3, p7, p6, p2])
    wall3 = Polygon([p0, p4, p7, p3])
    ceiling = Polygon([p4, p5, p6, p7])

    sld = Solid([floor, wall0, wall1, wall2, wall3, ceiling])

    ptest = Point(0.5, 0.5, 0.5)
    assert sld.is_point_inside(ptest) is True
    ptest = Point(-0.5, 0.5, 0.5)
    assert sld.is_point_inside(ptest) is False
    ptest = Point(0.0, 0.0, -0.5)
    assert sld.is_point_inside(ptest) is False


if __name__ == "__main__":
    test_point_inside()
