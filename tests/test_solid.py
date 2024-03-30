import pytest

from building3d import random_id
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

    floor = Polygon(random_id(), [p0, p3, p2, p1])
    wall0 = Polygon(random_id(), [p0, p1, p5, p4])
    wall1 = Polygon(random_id(), [p1, p2, p6, p5])
    wall2 = Polygon(random_id(), [p3, p7, p6, p2])
    wall3 = Polygon(random_id(), [p0, p4, p7, p3])
    ceiling = Polygon(random_id(), [p4, p5, p6, p7])

    _ = Solid(random_id(), [floor, wall0, wall1, wall2, wall3, ceiling])


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

    floor = Polygon(random_id(), [p0, p3, p2, p1])
    wall0 = Polygon(random_id(), [p0, p1, p5, p4])
    wall1 = Polygon(random_id(), [p1, p2, p6, p5])
    wall2 = Polygon(random_id(), [p3, p7, p6, p2])
    wall3 = Polygon(random_id(), [p0, p4, p7, p3])
    # Make ceiling too high (not attached to walls)
    ceiling = Polygon(random_id(), [p4err, p5err, p6err, p7err])

    with pytest.raises(GeometryError):
        _ = Solid(random_id(), [floor, wall0, wall1, wall2, wall3, ceiling])


def test_point_inside():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    p4 = Point(0.0, 0.0, 1.0)
    p5 = Point(1.0, 0.0, 1.0)
    p6 = Point(1.0, 1.0, 1.0)
    p7 = Point(0.0, 1.0, 1.0)

    floor = Polygon(random_id(), [p0, p3, p2, p1])
    wall0 = Polygon(random_id(), [p0, p1, p5, p4])
    wall1 = Polygon(random_id(), [p1, p2, p6, p5])
    wall2 = Polygon(random_id(), [p3, p7, p6, p2])
    wall3 = Polygon(random_id(), [p0, p4, p7, p3])
    ceiling = Polygon(random_id(), [p4, p5, p6, p7])

    sld = Solid(random_id(), [floor, wall0, wall1, wall2, wall3, ceiling])

    ptest = Point(0.5, 0.5, 0.5)
    assert sld.is_point_inside(ptest) is True
    ptest = Point(-0.5, 0.5, 0.5)
    assert sld.is_point_inside(ptest) is False
    ptest = Point(0.0, 0.0, -0.5)
    assert sld.is_point_inside(ptest) is False
    ptest = Point(0.0, 0.0, 0.0)  # This point is in the corner of the solid...
    assert sld.is_point_inside(ptest) is False  # ...so it is not inside
    assert sld.is_point_at_the_boundary(ptest) is True


def test_bounding_box():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    p4 = Point(0.0, 0.0, 1.0)
    p5 = Point(1.0, 0.0, 1.0)
    p6 = Point(1.0, 1.0, 1.0)
    p7 = Point(0.0, 1.0, 1.0)

    floor = Polygon(random_id(), [p0, p3, p2, p1])
    wall0 = Polygon(random_id(), [p0, p1, p5, p4])
    wall1 = Polygon(random_id(), [p1, p2, p6, p5])
    wall2 = Polygon(random_id(), [p3, p7, p6, p2])
    wall3 = Polygon(random_id(), [p0, p4, p7, p3])
    ceiling = Polygon(random_id(), [p4, p5, p6, p7])

    sld = Solid(random_id(), [floor, wall0, wall1, wall2, wall3, ceiling])
    pmin, pmax = sld.bounding_box()
    assert pmin.x == 0.0 and pmin.y == 0.0 and pmin.z == 0.0
    assert pmax.x == 1.0 and pmax.y == 1.0 and pmax.z == 1.0


if __name__ == "__main__":
    test_point_inside()
