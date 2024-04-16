import pytest

from building3d.geom.exceptions import GeometryError
from building3d.geom.plane import are_points_coplanar
from building3d.geom.point import Point


def test_are_points_coplanar():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(2.0, 0.5, 0.0)
    p3 = Point(2.0, -1.0, 0.0)
    p4 = Point(0.0, 0.0, 1.0)

    assert are_points_coplanar(p0, p1, p2, p3) is True
    assert are_points_coplanar(p3, p1, p2, p0) is True
    assert are_points_coplanar(p0, p1, p2) is True
    assert are_points_coplanar(p0, p1, p3) is True
    assert are_points_coplanar(p1, p2, p3) is True
    with pytest.raises(GeometryError):
        _ = are_points_coplanar(p0, p1)
        _ = are_points_coplanar(p0)
    assert are_points_coplanar(p0, p1, p2, p4) is False
    assert are_points_coplanar(p0, p1, p2, p3, p4) is False