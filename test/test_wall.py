import numpy as np
import pytest

from building3d.geom.exceptions import GeometryError
from building3d.geom.point import Point
from building3d.geom.wall import Wall


def test_too_few_points():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    wall = Wall("wall0", [p0, p1])

    with pytest.raises(GeometryError):
        wall.verify()


def test_points_not_coplanar():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(6.0, 6.0, 6.0)
    wall = Wall("wall0", [p0, p1, p2, p3])
    with pytest.raises(GeometryError):
        wall.verify()


def test_area():
    eps = 1e-6

    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    wall = Wall("wall", [p0, p1, p2, p3])
    expected_area = 1.0
    assert np.abs(wall.area() - expected_area) < eps

    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(0.0, 1.0, 0.0)
    wall = Wall("wall", [p0, p1, p2])
    expected_area = 0.5
    assert np.abs(wall.area() - expected_area) < eps

    p1 = Point(1.0, 0.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    p5 = Point(1.0, 0.0, 1.0)
    p7 = Point(0.0, 1.0, 1.0)
    wall = Wall("wall", [p1, p3, p7, p5])
    expected_area = np.sqrt(2)
    assert np.abs(wall.area() - expected_area) < eps


def test_centroid():
    eps = 1e-6

    p1 = Point(1.0, 0.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    p5 = Point(1.0, 0.0, 1.0)
    p7 = Point(0.0, 1.0, 1.0)
    wall = Wall("wall", [p1, p3, p7, p5])
    expected_centroid = np.array([0.5, 0.5, 0.5])
    assert np.sum(wall.centroid - expected_centroid) < eps


def test_triangulation():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(2.0, 0.0, 0.0)
    p2 = Point(2.0, 1.0, 0.0)
    p3 = Point(1.0, 1.0, 0.0)
    p4 = Point(1.0, 2.0, 0.0)
    p5 = Point(0.0, 2.0, 0.0)
    wall = Wall("L-shaped_wall", [p0, p1, p2, p3, p4, p5])
    triangles = [{i, j, k} for i, j, k in wall.triangles]
    assert {2, 3, 4} not in triangles
