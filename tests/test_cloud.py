import numpy as np
import pytest

from building3d.geom.cloud import are_points_coplanar
from building3d.geom.cloud import are_points_in_set
from building3d.geom.cloud import array_to_points
from building3d.geom.cloud import points_to_array
from building3d.geom.exceptions import GeometryError
from building3d.geom.point import Point


def test_points_to_array():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 1.0, 1.0)
    p2 = Point(2.0, 2.0, 2.0)
    p3 = Point(3.0, 3.0, 3.0)
    arr = points_to_array([p0, p1, p2, p3])
    assert arr.shape == (4, 3)
    assert (arr[0] == p0.vector()).all()


def test_array_to_points():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 1.0, 1.0)
    arr = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 1.0, 1.0],
        ]
    )
    pts = array_to_points(arr)
    assert pts[0] == p0
    assert pts[1] == p1


def test_are_points_in_set():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 1.0, 1.0)
    p2 = Point(2.0, 2.0, 2.0)
    p3 = Point(3.0, 3.0, 3.0)
    cloud1 = [p0, p1]
    cloud2 = [p0, p1, p2, p3]
    assert are_points_in_set(cloud1, cloud2)
    assert not are_points_in_set(cloud2, cloud1)


def test_are_points_coplanar():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(2.0, 0.5, 0.0)
    p3 = Point(2.0, -1.0, 0.0)
    p4 = Point(0.0, 0.0, 1.0)

    assert are_points_coplanar(p0, p0, p0, p0) is True
    assert are_points_coplanar(p0, p1, p2, p3) is True
    assert are_points_coplanar(p3, p1, p2, p0) is True
    assert are_points_coplanar(p0, p1, p2) is True
    assert are_points_coplanar(p0, p1, p3) is True
    assert are_points_coplanar(p1, p2, p3) is True
    assert are_points_coplanar(p0, p1) is True
    assert are_points_coplanar(p0) is True
    assert are_points_coplanar(p0, p1, p2, p4) is False
    assert are_points_coplanar(p0, p1, p2, p3, p4) is False


def test_are_points_coplanar_for_colinear_points():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(2.0, 0.0, 0.0)
    p3 = Point(3.0, 0.0, 0.0)
    assert are_points_coplanar(p0, p1, p2, p3) is True
